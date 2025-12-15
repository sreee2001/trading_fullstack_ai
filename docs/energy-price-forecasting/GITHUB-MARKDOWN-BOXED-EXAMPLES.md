# GitHub Markdown Boxed/Bordered Layout Examples

This document shows various ways to create boxed or bordered visual layouts in GitHub markdown.

---

## Method 1: Using Blockquotes (Recommended - Simple & Reliable)

Blockquotes create a nice left border and indentation:

```markdown
> **🔮 Energy Price Forecasting System**
> 
> A production-ready ML system for forecasting energy commodity prices
> 
> **Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow
> 
> **Progress**: 20/64 features (31.3%) | 85%+ test coverage | 98%+ data quality
```

**Result:**
> **🔮 Energy Price Forecasting System**
> 
> A production-ready ML system for forecasting energy commodity prices
> 
> **Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow
> 
> **Progress**: 20/64 features (31.3%) | 85%+ test coverage | 98%+ data quality

---

## Method 2: Using HTML `<details>` Tag (Collapsible Box)

Creates a collapsible section with a border-like appearance:

```markdown
<details>
<summary><b>Click to expand project details</b></summary>

**🔮 Energy Price Forecasting System**

A production-ready ML system for forecasting energy commodity prices

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

**Progress**: 20/64 features (31.3%) | 85%+ test coverage | 98%+ data quality

</details>
```

**Result:**
<details>
<summary><b>Click to expand project details</b></summary>

**🔮 Energy Price Forecasting System**

A production-ready ML system for forecasting energy commodity prices

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

**Progress**: 20/64 features (31.3%) | 85%+ test coverage | 98%+ data quality

</details>

---

## Method 3: Using HTML `<div>` with Inline Styles (Limited Support)

GitHub has limited CSS support, but some styles work:

```markdown
<div style="border: 2px solid #0366d6; border-radius: 8px; padding: 16px; background-color: #f6f8fa;">

**🔮 Energy Price Forecasting System**

A production-ready ML system for forecasting energy commodity prices

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

</div>
```

**Result:**
<div style="border: 2px solid #0366d6; border-radius: 8px; padding: 16px; background-color: #f6f8fa;">

**🔮 Energy Price Forecasting System**

A production-ready ML system for forecasting energy commodity prices

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

</div>

---

## Method 4: Using Table as Border (Most Compatible)

Tables can create a boxed appearance:

```markdown
<table>
<tr>
<td>

**🔮 Energy Price Forecasting System**

A production-ready ML system for forecasting energy commodity prices

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

</td>
</tr>
</table>
```

**Result:**
<table>
<tr>
<td>

**🔮 Energy Price Forecasting System**

A production-ready ML system for forecasting energy commodity prices

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

</td>
</tr>
</table>

---

## Method 5: Using Code Block with ASCII Art

Creates a visual box using ASCII characters:

```markdown
```
┌─────────────────────────────────────────────────────────┐
│  🔮 Energy Price Forecasting System                    │
│                                                         │
│  A production-ready ML system for forecasting          │
│  energy commodity prices                               │
│                                                         │
│  Tech Stack: Python • TensorFlow • PostgreSQL • MLflow │
│  Progress: 20/64 features (31.3%)                      │
└─────────────────────────────────────────────────────────┘
```
```

**Result:**
```
┌─────────────────────────────────────────────────────────┐
│  🔮 Energy Price Forecasting System                    │
│                                                         │
│  A production-ready ML system for forecasting          │
│  energy commodity prices                               │
│                                                         │
│  Tech Stack: Python • TensorFlow • PostgreSQL • MLflow │
│  Progress: 20/64 features (31.3%)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Method 6: Using Horizontal Rules and Centering

Combines horizontal rules with centered content:

```markdown
---

<div align="center">

**🔮 Energy Price Forecasting System**

*A production-ready ML system for forecasting energy commodity prices*

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

</div>

---
```

**Result:**

---

<div align="center">

**🔮 Energy Price Forecasting System**

*A production-ready ML system for forecasting energy commodity prices*

**Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

</div>

---

## Method 7: Nested Blockquotes (Double Border Effect)

```markdown
> > **🔮 Energy Price Forecasting System**
> > 
> > A production-ready ML system for forecasting energy commodity prices
> > 
> > **Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow
```

**Result:**
> > **🔮 Energy Price Forecasting System**
> > 
> > A production-ready ML system for forecasting energy commodity prices
> > 
> > **Tech Stack**: Python • TensorFlow/Keras • PostgreSQL/TimescaleDB • MLflow

---

## Recommended Approach for GitHub Profile

For GitHub profile READMEs, I recommend **Method 1 (Blockquotes)** or **Method 2 (Details tag)** because:

1. ✅ **Reliable**: Works consistently across all GitHub markdown renderers
2. ✅ **Simple**: Easy to maintain and edit
3. ✅ **Clean**: Professional appearance
4. ✅ **Accessible**: Works on all devices and screen readers

### Example Implementation:

```markdown
## 🔮 Energy Price Forecasting System

[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()
[![Epic 1](https://img.shields.io/badge/Epic%201-Complete-success)]()

> **A production-ready ML system** forecasting WTI crude oil, Brent crude, and natural gas prices using multi-source data, advanced ML models (ARIMA, Prophet, LSTM), and comprehensive backtesting.
> 
> **Tech Stack**: `Python` • `TensorFlow/Keras` • `PostgreSQL/TimescaleDB` • `MLflow`
> 
> **Progress**: `20/64 features (31.3%)` | `85%+ test coverage` | `98%+ data quality`
> 
> 📖 [Documentation](docs/) • 🧪 [Test Cases](docs/test-cases/)
```

---

## Tips for Best Results

1. **Use blockquotes** for simple bordered sections
2. **Use `<details>` tags** for collapsible content
3. **Combine with badges** for visual appeal
4. **Use horizontal rules** (`---`) to separate sections
5. **Center content** with `<div align="center">` for emphasis
6. **Use code formatting** (backticks) for inline highlights

---

**Last Updated**: December 15, 2025

