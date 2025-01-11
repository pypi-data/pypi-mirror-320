## Eazyml Explainable AI
![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)  ![PyPI package](https://img.shields.io/badge/pypi%20package-0.0.45-brightgreen) ![Code Style](https://img.shields.io/badge/code%20style-black-black)

![EazyML](https://eazyml.com/static/media/EazyML%20XAI%20blue.b7696b7a.png)

It provides explanations for a model's prediction, based on provided train and test data files.

### Features
- It provides explanations for a model's prediction, based on provided train and test data files.
### APIs
It provides following apis :

1. scikit_feature_selection
    ```python
    ez_explain(
            mode='classification',
            outcome='target',
            train_file_path='train.csv',
            test_file_path='test.csv',
            model=my_model,
            data_type_dict=data_type_dict,
            selected_features_list=lis_of_derived_features,
            options={"data_source": "parquet", "record_number": [1, 2, 3]})

### Useful Links
- [Documentation](https://docs.eazyml.com)
- [Homepage](https://eazyml.com)
- If you have more questions or want to discuss a specific use case please book an appointment [here](https://eazyml.com/trust-in-ai)

#### License
This project is licensed under the [Proprietary License](https://github.com/EazyML/eazyml-docs/blob/master/LICENSE).

---

*Maintained by [EazyML](https://eazyml.com)*  
*© 2025 EazyML. All rights reserved.*
