[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/petrobras/BibMon/HEAD)
[![Apache 2.0][apache-shield]][apache] 
[![CC BY 4.0][cc-by-shield]][cc-by]

[apache]: https://opensource.org/licenses/Apache-2.0
[apache-shield]: https://img.shields.io/badge/License-Apache_2.0-blue.svg
[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

# BibMon

`BibMon` (from the Portuguese ***Bib**lioteca de **Mon**itoramento de Processos*, or Process Monitoring Library) is a Python package that provides deviation-based predictive models for fault detection, soft sensing, and process condition monitoring.

For further information, please refer to the [documentation](https://bibmon.readthedocs.io/) or to the [scientific publication](https://www.sciencedirect.com/science/article/pii/S2772508124000449) detailing `BibMon`.

Installation
----------------------

`BibMon` can be installed using [pip](https://pypi.org/project/bibmon/):

    pip install bibmon

Or [conda](https://anaconda.org/conda-forge/bibmon):

    conda install conda-forge::bibmon

Available Models
----------------------

* PCA (Principal Component Analysis);
* ESN (Echo State Network);
* SBM (Similarity-Based Method);
* Autoencoders;
* any regressor that uses the `scikit-learn` interface.

Usage
----------------------

Essentially, the library is used in two steps:

1. In the training step, a model is generated that captures the relationships between variables in the normal process condition;
2. In the prediction step, process data is compared to the model's predictions, resulting in deviations; if these deviations exceed a predefined limit, alarms are triggered.

Specifically, the implemented control charts are based on squared prediction error (SPE).

For more details, please refer to the [tutorials](https://bibmon.readthedocs.io/en/latest/tutorials.html) available in the documentation to learn about the main functionalities of `BibMon`. You can find the corresponding Jupyter Notebooks for these tutorials in the `docs/source/` directory.


Features
----------------------

The resources offered by `BibMon` are:

* Application in online systems: a trained `BibMon` model can be used for online analysis with both individual samples and data windows. For each sample or window, a prediction is made, the model state is updated, and alarms are calculated.
* Compatibility, within the same architecture, of regression models (i.e., virtual sensors, containing separate X and Y data, such as RandomForest) and reconstruction models (containing only X data, such as PCA).
* Preprocessing pipelines that take into account the differences between X and Y data and between training and testing stages.
* Possibility of programming different alarm logics.
* Easy extensibility through inheritance (there is a class called `GenericModel` that implements all the common functionality for various models and can be used as a base for implementing new models). For details, consult the `CONTRIBUTING.md` file.
* Convenience functions for performing automatic offline analysis and plotting control charts.
* Real and simulated process datasets available for importing.
* Comparative tables to automate the performance analysis of different models.
* Automatic hyperparameter tuning.

Contributing
----------------------

BibMon is an open-source project driven by the community. If you would like to contribute to the project, please refer to the [CONTRIBUTING.md](https://github.com/petrobras/bibmon/blob/main/CONTRIBUTING.md) file.

The package originated from research projects conducted in collaboration between the Chemical Engineering Program at COPPE/UFRJ and the Leopoldo Américo Miguez de Mello Research Center (CENPES/Petrobras).
