using UnityEngine;

public class LightingManager : MonoBehaviour
{
    private float _currentValue;
    private static readonly int Blend = Shader.PropertyToID("_Blend");
    [SerializeField] private Material skybox;
    [SerializeField] private Light lightSource;
    [SerializeField] private ReflectionProbe reflectionProbe;

    public void UpdateLighting(float val)
    {
        if (_currentValue == val)
        {
            return;
        }
        
        SetMaterial(val);
        SetLightSource(val);
        reflectionProbe.RenderProbe();
        _currentValue = val;
    }

    private void SetMaterial(float val)
    {
        skybox.SetFloat(Blend, val);
    }
    
    private void SetLightSource(float val)
    {
        lightSource.intensity = Mathf.Lerp(0.2f, 1.5f, val);
    }
}
