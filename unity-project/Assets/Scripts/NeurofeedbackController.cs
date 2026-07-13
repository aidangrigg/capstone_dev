using System;
using System.Collections.Generic;
using UnityEngine;
using NativeWebSocket;
using UnityEngine.InputSystem;

[Serializable]
public class NeurofeedbackWebsocketPacket
{
    public float faa;
    public float theta;

    public static NeurofeedbackWebsocketPacket CreateFromJson(string jsonString)
    {
        return JsonUtility.FromJson<NeurofeedbackWebsocketPacket>(jsonString);
    }
}

public class RunningStats
{
    private readonly double _outlierZThreshold;
    private double _mean;
    private double _m2;

    public int Count { get; private set; }
    public double Mean => Count == 0 ? 0.0 : _mean;

    public double Variance => Count < 2 ? 0.0 : _m2 / (Count - 1);
    public double StdDev => Math.Sqrt(Variance);

    public RunningStats(double outlierZThreshold = 3.0)
    {
        if (outlierZThreshold <= 0) throw new ArgumentOutOfRangeException(nameof(outlierZThreshold));

        _outlierZThreshold = outlierZThreshold;
    }

    /// <summary>
    /// Attempts to add a value. Returns false if full or if the value is an outlier.
    /// </summary>
    public bool TryAdd(double value)
    {
        Count++;
        var delta = value - _mean;
        _mean += delta / Count;
        var delta2 = value - _mean;
        _m2 += delta * delta2;

        return true;
    }

    /// <summary>
    /// Returns true if the value is a statistical outlier relative to the current distribution.
    /// Values are never considered outliers until there are enough points to assess spread.
    /// </summary>
    public bool IsOutlier(double value)
    {
        if (Count < 2) return false;
        var std = StdDev;
        if (std == 0) return false;
        return Math.Abs(value - _mean) > _outlierZThreshold * std;
    }

    public void Reset()
    {
        Count = 0;
        _mean = 0.0;
        _m2 = 0.0;
    }

    public override string ToString() =>
        $"Count={Count}, Mean={Mean:F4}, StdDev={StdDev:F4}";
}

public enum FeedbackSources
{
    Light,
    Wind,
    Waves
}


public class NeurofeedbackController : MonoBehaviour
{
    public enum ControllerState
    {
        Idle,
        ComputingBaseline
    }
    
    [SerializeField] private LightingManager lightingManager;
    [SerializeField] private WaveManager waveManager;
    [SerializeField] private WindManager windManager;
    [SerializeField] private bool manualControl;
    [SerializeField, Range(-1f, 1f)] private float waveLevel;
    [SerializeField, Range(-1f, 1f)] private float windLevel;
    [SerializeField, Range(-1f, 1f)] private float lightLevel;

    public ControllerState State { get; set; }
    private HashSet<FeedbackSources> _activeFeedbacks;
    
    private RunningStats _faaStats, _thetaStats;
    private WebSocket _websocket;

    private async void Start()
    {
        Application.runInBackground = true;

        _activeFeedbacks = new HashSet<FeedbackSources>();

        _faaStats = new RunningStats();
        _thetaStats = new RunningStats();

        _websocket = new WebSocket("ws://localhost:1234");
        _websocket.OnOpen += () => Debug.Log("Connection open!");
        _websocket.OnError += (e) => Debug.Log("Error! " + e);
        _websocket.OnClose += (code) => Debug.Log($"Connection closed! Code={code}");
        _websocket.OnMessage += HandleMessage;
        await _websocket.Connect();
    }

    private void Update()
    {
        if (manualControl)
        {
            lightingManager.UpdateLighting(lightLevel);
            waveManager.UpdateWaveStrength(waveLevel);
            windManager.UpdateWindStrength(windLevel);
        }
    }

    public void EnableFeedback(FeedbackSources source)
    {
        _activeFeedbacks.Add(source);
    }
    
    public void DisableFeedback(FeedbackSources source)
    {
        _activeFeedbacks.Remove(source);
    }

    public void ResetFeedbackLevels()
    {
        waveLevel = 0.0f;
        windLevel = 0.0f;
        lightLevel = 0.0f;
    }

    private float MapFeedbackValue(RunningStats stats, float rawReading)
    {
        var mean = stats.Mean;
        var std = stats.StdDev;
        var t = Mathf.InverseLerp((float)(mean - std), (float)(mean + std), rawReading);
        return Mathf.Lerp(-1, 1, t);
    }

    private void HandleFeedbackUpdate(float faaReading, float thetaReading)
    {
        foreach (var feedback in _activeFeedbacks)
        {
            switch (feedback)
            {
                case FeedbackSources.Light:
                    lightLevel = MapFeedbackValue(_faaStats, faaReading);
                    break;
                case FeedbackSources.Wind:
                    windLevel = MapFeedbackValue(_thetaStats, thetaReading);
                    break;
            }
        }
        
        Debug.Log($"Updated lighting to {lightLevel}, wind level to {windLevel}, and wave strength to {waveLevel}");
        
        lightingManager.UpdateLighting(lightLevel);
        windManager.UpdateWindStrength(windLevel);
        waveManager.UpdateWaveStrength(waveLevel);
    }
    
    private void HandleMessage(byte[] bytes)
    {
        if (manualControl)
        {
            return;
        }
        
        var message = System.Text.Encoding.UTF8.GetString(bytes);
        var packet = NeurofeedbackWebsocketPacket.CreateFromJson(message);

        switch (State)
        {
            case ControllerState.ComputingBaseline:
                Debug.Log($"Computing baseline with values {packet.faa}, {packet.theta}");
                _faaStats.TryAdd(packet.faa);
                _thetaStats.TryAdd(packet.theta);
                break;
            case ControllerState.Idle:
                HandleFeedbackUpdate(packet.faa, packet.theta);
                break;
        }
    }

    private async void OnApplicationQuit()
    {
        await _websocket.Close();
    }
}