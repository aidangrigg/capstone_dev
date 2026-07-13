using UnityEngine;

public class WindManager : MonoBehaviour
{

    private float _currentValue;
    [SerializeField] private AudioSource windAudioSource;
    
    public void UpdateWindStrength(float val)
    {
        if (_currentValue == val)
        {
            return;
        }
        
        SetAudioVolume(val);
        _currentValue = val;
    }

    private void SetAudioVolume(float val)
    {
        val = Mathf.InverseLerp(-1, 1, val);
        windAudioSource.volume = Mathf.Lerp(0.0f, 1.0f, val);
    }
}
