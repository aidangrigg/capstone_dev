# Todo
- [x] Refactoring nf processing proj.
- [x] Websocket (nf processing -> unity proj.)
- [x] Unity project
  - [x] Scenario development (beach, something else with free 3D files online)
  - [ ] Websocket connection
  - [ ] Adjust light/sound levels based on values from ws
- [ ] Affix electrodes in correct positions
  - [ ] Either with swim cap, or 3d printed holder to connect to VR strap
- [ ] Test new EEG (waiting on electrodes from YK)


# New protocols

Same previous steps:

(around 10Hz)
- lsl_node: Connects to LSL, pulls in samples async. Filters these samples (bandpass, notch), emits signal when new samples available

(20Hz)
- NeurofeedbackProcessing:
  - This is now our BiomarkerManager (kinda the controller). This will
    be able to create a Biomarker (kinda the model) (and store the
    widget + processing thing).
  - Each biomarker will have an ID, widgets will emit signals up to
    the biomarker manager to remove things. The biomarker manager will
    then emit its own signal to signal everything else to clean up.
  - BiomarkerManager will instantiate the correct widget, and then
    pass it to the view to draw.

- MainView
  - Will have a reference to biomarker manager in the constructor.
  - Will connect to the biomarker add & delete widget signals
  - When the biomarker manager creates a new plot widget, a function
    in this class will be called (a ref to the widget). The widget
    will be a base class that only has a *.widget()* and *.id()*
    functions. The class will draw the widget with .widget(), and
    delete the correct widget by finding it by id.

- BiomarkerWidget
  - In the constructor, the widget will take in its associated
    BiomarkerProcessor.
  - Each will have an update function, that redraws the widget from
    the processing model.
  - The widget will also have a settings button, which when clicked
    will open a dialog. After the dialog is changed, will emit a
    settings_changed signal that will be handled by the view, then
    passed to the controller, after which is handled to the processor.
    - TBH, could just update the processor directly if we're passing
      in a ref though its not very MVC since the view would directly
      update our weird model.
    - This would make it easier and cleaner though so idc.
