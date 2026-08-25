# 🧠 Life-OS — Wellbeing Dashboard

> **Your screen time. Your habits. Your reality.**

A Streamlit-based personal wellbeing dashboard that turns daily screen-time data into actionable lifestyle insights using **Pandas, data visualization, and Google Gemini**.

Life-OS doesn't simply tell you to *"use your phone less."*  
It analyzes where your time is going, compares it against your personal goal, and uses Gemini as a **brutal-but-fair AI life coach** to suggest realistic, physical, real-world alternatives.

---

## 🚀 Live Demo

**Try Life-OS:**  
[Open the Live Dashboard](YOUR_STREAMLIT_DEPLOYMENT_URL)

> Replace `YOUR_STREAMLIT_DEPLOYMENT_URL` with your actual Streamlit deployment URL before submission.

---

## 🎯 Problem

Digital addiction and excessive screen time have become common problems.

Most screen-time reports simply show numbers such as:

> "You spent 5 hours on your phone today."

But numbers alone don't necessarily lead to behavioral change.

The real question is:

> **What should I actually do differently with those 5 hours?**

Life-OS addresses this gap by combining **data visualization + personalized AI coaching**.

---

# 💡 Solution

Life-OS works as a personal wellbeing command center.

The application:

1. Loads daily screen-time data from a CSV dataset.
2. Allows the user to select a specific day.
3. Lets the user define a personal daily screen-time goal.
4. Calculates important daily metrics.
5. Visualizes screen-time trends.
6. Aggregates the day's usage into structured data.
7. Sends the summarized data to Gemini.
8. Generates personalized lifestyle recommendations.
9. Suggests concrete real-world replacements for excessive screen time.
10. Generates a shareable accountability URL containing the day's statistics.

---

# ✨ Key Features

## 📊 1. Personal Wellbeing Dashboard

The dashboard provides a SaaS-style command center for understanding daily screen usage.

It displays:

- Total screen time
- Most-used application
- Screen time vs daily goal
- Category breakdown
- 14-day usage trend

---

## 🎯 2. Custom Daily Screen-Time Goal

The sidebar provides a configurable daily goal.

Users can choose a maximum screen-time target between:

**30–480 minutes**

The dashboard automatically compares actual usage against the selected goal.

---

## 📱 3. Most-Used App Detection

For the selected day, Life-OS identifies the application that consumed the most time.

Example:

```text
Most Used App
YouTube
127 min