using System;
using System.Collections.Generic;
using NativeWebSocket;
using UnityEngine;

[Serializable]
public class CommandPacket
{
    public string command;
    public List<string> args;

    public static CommandPacket CreateFromJson(string jsonString)
    {
        return JsonUtility.FromJson<CommandPacket>(jsonString);
    }
}

public class ExperimentController : MonoBehaviour
{
    [SerializeField] private string controlServerUrl = "ws://localhost:42069";
    [SerializeField] private NeurofeedbackController neurofeedbackController;
    
    private WebSocket _wsControlServer;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    private async void Start()
    {
        Application.runInBackground = true;

        _wsControlServer = new WebSocket(controlServerUrl);
        _wsControlServer.OnOpen += () => Debug.Log("Connection with the control server established!");
        _wsControlServer.OnClose += (code) => Debug.Log($"Connection with the control server closed! Code={code}");
        _wsControlServer.OnError += (e) => Debug.Log("Error! " + e);
        _wsControlServer.OnMessage += HandleMessage;
        await _wsControlServer.Connect();
    }

    private void HandleFeedbackCommand(CommandPacket packet, bool enable)
    {
        FeedbackSources feedback;
        switch (packet.args[0])
        {
            case "light":
                Debug.Log("light feedback source");
                feedback = FeedbackSources.Light;
                break;
            case "wind":
                Debug.Log("wind feedback source");
                feedback = FeedbackSources.Wind;
                break;
            default: return;
        }

        if (enable)
        {
            neurofeedbackController.EnableFeedback(feedback);
        }
        else
        {
            neurofeedbackController.DisableFeedback(feedback);
            neurofeedbackController.ResetFeedbackLevels();
        }
    }

    private void HandleMessage(byte[] bytes) 
    {
        var message = System.Text.Encoding.UTF8.GetString(bytes);
        var packet = CommandPacket.CreateFromJson(message);
        
        Debug.Log($"Control message received: {message}");

        switch (packet.command)
        {
            case "baseline_start":
                neurofeedbackController.State = NeurofeedbackController.ControllerState.ComputingBaseline;
                break;
            case "baseline_end":
                // TODO: Could also remove all the feedbacks here
                neurofeedbackController.State = NeurofeedbackController.ControllerState.Idle;
                break;
            case "feedback_enable":
                HandleFeedbackCommand(packet, true);
                break;
            case "feedback_disable":
                HandleFeedbackCommand(packet, false);
                break;
        }
    }
    
    private async void OnApplicationQuit()
    {
        await _wsControlServer.Close();
    }
}
