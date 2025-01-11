## Eazyml Image Explainable AI 
![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)  ![PyPI package](https://img.shields.io/badge/pypi%20package-0.0.19-brightgreen) ![Code Style](https://img.shields.io/badge/code%20style-black-black)

![EazyML](EazyML_logo.png)

This package focuses on segmentation prediction, explainability, active learning and online learning for image dataset.

### Features
- Active learning focuses on reducing the amount of labeled data required to train the model while maximizing performance, making it particularly useful when labeling data is expensive or time-consuming. By prioritizing uncertain or diverse examples, active learning accelerates model improvement and enhances efficiency.
- Online learning is a machine learning approach where models are trained incrementally as data becomes available, rather than using a fixed, pre-existing dataset. This method is well-suited for dynamic environments, enabling real-time updates and adaptability to new patterns or changes in data streams.

### APIs
It provides following apis :

1. ez_image_active_learning :
This API sorts test images based on explainability scores for the model’s predictions. If a “query count” is specified in the options, it returns the indices and corresponding scores for that number of inputs.

    ```python
    ez_image_active_learning(
            filenames=['..', '..'],
            model_path='path_of_model',
            predicted_filenames=['path_of_model_prediction_file_names'],
            options={
                "query_count": 10,
                "training_data_path": "path/to/training/data.csv",
                "score_strategy": "weighted-moments",
                "al_strategy": "pool-based",
                "xai_strategy": "gradcam",
                "gradcam_layer": "layer_name",
                "model_num": "1"
            }
        )
    ```

2. ez_image_model_evaluate :
This API validates a model using provided data and returns the model evaluation.
    ```python
    ez_image_model_evaluate(
            validation_data_path='path_of_new_data_for_validation',
            model_path='path_of_model',
            options={
                "required_functions": {
                    "loss_fn": '...',
                    "metric_fns": '...',
                    "input_preprocess_fn": '',
                    "label_preprocess_fn": '',
                    "output_process_fn": ''
                    },
                "batch_size": 32,
                "log_file": "path/to/log/file"
            })
    ```

3. ez_image_online_learning :
This API updates a given model using new training data and saves the updated model. The update process adapts based on the Online Learning strategy or optimizes performance on provided validation data.
    ```python
    ez_image_online_learning(
            validation_data_path='path_of_new_data_for_validation',
            model_path='path_of_model',
            options={
                "required_functions": {
                    "loss_fn": '...',
                    "metric_fns": '...',
                    "input_preprocess_fn": '',
                    "label_preprocess_fn": '',
                    "output_process_fn": ''
                },
                "batch_size": 32,
                "log_file": "path/to/log/file"
            }
        )
    ```

4. ez_xai_image_explain :
This API provides confidence scores and image explanations for model predictions. It can process a single image or multiple images, returning explanations for all predictions.
    ```python
    ez_xai_image_explain(
            filenames=['..', '..'],
            model_path='path_of_model',
            predicted_filenames=['path_of_model_prediction_file_names'],
            options={
                "training_data_path": "...",
                "score_strategy": "weighted-moments",
                "xai_strategy": "gradcam",
                "xai_image_path": "...",
                "gradcam_layer": "layer_name",
                "model_num": "1",
                "required_functions": {...}
            }
        )
    ```


### Useful Links
- [Documentation](https://docs.eazyml.com)
- [Homepage](https://eazyml.com)
- If you have more questions or want to discuss a specific use case please book an appointment [here](https://eazyml.com/trust-in-ai)

#### License
This project is licensed under the [Proprietary License](LICENSE).

---

*Maintained by [EazyML](https://eazyml.com)*  
*© 2025 EazyML. All rights reserved.*


