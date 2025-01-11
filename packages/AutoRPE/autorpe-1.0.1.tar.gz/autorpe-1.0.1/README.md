# AutoRPE

![AutoRPE Logo](docs/source/images/logo.png)
*(Automatic Reduced Precision Emulator)*

AutoRPE is a tool designed to optimize the numerical precision of computational science models written in Fortran. Originally developed to enable the use of a [Reduced Precision Emulator](https://rpe.readthedocs.io/en/stable/) (RPE) ( [Dawson, A. and Düben, P. D.: 2017](https://gmd.copernicus.org/articles/10/2221/2017/)) in large-scale codes such as NEMO, AutoRPE has since evolved into a framework for streamlining code modifications, managing precision experiments, and facilitating precision sensitivity analysis.

## Features

- **Automatic Code Manipulation:**

Modifies Fortran source code to implement reduced precision emulation, reducing manual effort.

- **Precision Sensitivity Analysis:**

Identifies sensitive variables requiring higher precision using algorithms like binary search.

- **Workflow Management:**

Automates precision testing workflows to minimize manual intervention and ensure reproducibility.

- **Code Coherency Assurance:**

Detects and resolves inconsistencies in variable types to ensure code correctness.

## Background

Global warming and climate change pose significant challenges to humanity due to their social, economic, and environmental impacts. Better understanding and improved capacity to forecast climate evolution can support the development of ambitious adaptation policies. Earth system models (ESMs) are crucial for simulating and predicting climate behavior, but their computational demands continue to grow with advancements such as higher resolution and ensemble forecasting. Efficient use of computational resources has become essential, and mixed-precision approaches are emerging as a way to enhance performance by reducing memory and computational costs. However, identifying variables that can safely operate at reduced precision without compromising model accuracy is complex. AutoRPE was developed to automate this process, enabling the exploration of mixed-precision configurations in full-scale models and facilitating performance improvements in computationally intensive simulations.

## Documentation

For detailed documentation on installation, usage, and workflows, visit the [AutoRPE Documentation](https://autorpe.readthedocs.io).