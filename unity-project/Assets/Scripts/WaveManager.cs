using System.Globalization;
using UnityEngine;

public class WaveManager : MonoBehaviour
{

    private float _currentValue;
    private static readonly int WaveHeight = Shader.PropertyToID("_WaveHeight");
    
    [SerializeField] private Material waveShader;
    [SerializeField] private AudioSource waveAudioSource;
    
    public void UpdateWaveStrength(float val)
    {
        if (_currentValue == val)
        {
            return;
        }
        
        SetMaterial(val);
        SetAudioVolume(val);
        _currentValue = val;
    }

    private void SetAudioVolume(float val)
    {
        val = Mathf.InverseLerp(-1, 1, val);
        waveAudioSource.volume = Mathf.Lerp(0.1f, 0.5f, val);
    }

    private void SetMaterial(float val)
    {
        val = Mathf.InverseLerp(-1, 1, val);
        waveShader.SetFloat(WaveHeight, Mathf.Lerp(0.05f, 0.35f, val));
    }
}
