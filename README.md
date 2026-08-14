# Irrigation Water Requirement Prediction Using Linear Regression

## 📌 Project Overview

This project uses Machine Learning to predict irrigation requirements based on different soil, weather, crop, and field-related conditions.

A Linear Regression model is used to predict an irrigation-need score.

## 🎯 Objective

The main objective of this project is to understand how Machine Learning can be applied to an agriculture-related problem and to build a simple prediction model using Linear Regression.

## 📊 Dataset

The dataset contains information such as:

- Soil type
- Soil pH
- Soil moisture
- Organic carbon
- Temperature
- Humidity
- Rainfall
- Sunlight hours
- Wind speed
- Crop type
- Crop growth stage
- Season
- Field area
- Previous irrigation
- Region

The original `Irrigation_Need` values are:

- Low
- Medium
- High

For this Linear Regression project, these were converted into numerical scores:

- Low → 0
- Medium → 1
- High → 2

## 🤖 Model Used

**Linear Regression**

The dataset was divided into:

- 80% training data
- 20% testing data

Categorical features were converted into numerical features using one-hot encoding.

## 📈 Results

The model achieved:

- **Mean Absolute Error (MAE):** 0.295
- **R² Score:** 0.569

The R² score indicates that the model explains approximately 57% of the variation in the irrigation-need score.

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- KaggleHub
- Google Colab

## 🚀 What I Learned

Through this project, I learned how to:

- Load and explore a dataset
- Prepare data for Machine Learning
- Convert categorical data into numerical data
- Split data into training and testing sets
- Train a Linear Regression model
- Make predictions
- Evaluate a Machine Learning model using MAE and R²

## 👤 Author

Mriganka Banerjee
