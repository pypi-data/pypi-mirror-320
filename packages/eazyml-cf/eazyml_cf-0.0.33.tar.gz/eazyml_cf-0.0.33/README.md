## Eazyml Counterfactual
![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)  ![PyPI package](https://img.shields.io/badge/pypi%20package-0.0.32-brightgreen) ![Code Style](https://img.shields.io/badge/code%20style-black-black)

![EazyML](https://eazyml.com/static/media/EazyML%20XAI%20blue.b7696b7a.png)

EazyML revolutionizes machine learning by introducing counterfactual inference, automating the process of identifying optimal changes to variables that shift outcomes from unfavorable to favorable. This approach overcomes the limitations of manual "what-if" analysis, enabling models to provide actionable, prescriptive insights alongside their predictions.

### Features
- It performs feature selection from a training dataset by excluding specific columns and the target outcome column.
- This function builds a machine learning model using a specified training dataset.
- It provides platform to automates counterfactual inference for a test record by calculating the probability of an unfavorable outcome and determining the optimal adjustments to minimize it. It processes input datasets, configuration parameters, and model details to identify actionable changes in features while respecting constraints, enabling prescriptive insights for improved outcomes.
### APIs
It provides following apis :

1. scikit_feature_selection
    ```python
    sk_feature_selection(
        train_file = 'train/file/path.csv',
        outcome = 'outcome column name',
        config= {
                "discard_columns" : ['id', 'unnamed'],
                }
        )



2. scikit_model_building
    ```python
    sk_feature_selection(
        train_file = 'train/file/path.csv',
        test_file = 'test/file/path.csv',
        outcome = 'outcome column name',
        selected_columns = 'List of selected input features',
        config= {
            "unfavorable_outcome" : 1,
            "sklearn_classifier" : 'Gradient Boosting'
        }
    )



3. ez_cf_inference
    ```python
    ez_cf_inference(
        train_file = 'train/file/path.csv',
        test_file = 'test/file/path.csv',
        outcome = 'outcome column name',
        config= {
            "unfavorable_outcome" : 1,
            "lower_quantile" : 0.01,
                "upper_quantile" : 0.99,
                "p" : 40,
                "M" : 2,
                "N" : 10000,
                "tolerable_error_threshold" : 0.1
            },
            selected_columns = 'List of selected input features',
            model_info = 'dictionary of model information'
            test_record_idx = 'single or multiple testdata id or None'
        )



### Useful Links
- [Documentation](https://docs.eazyml.com)
- [Homepage](https://eazyml.com)
- If you have more questions or want to discuss a specific use case please book an appointment [here](https://eazyml.com/trust-in-ai)

#### License
This project is licensed under the [Proprietary License](https://github.com/EazyML/eazyml-docs/blob/master/LICENSE).

---

*Maintained by [EazyML](https://eazyml.com)*  
*© 2025 EazyML. All rights reserved.*
