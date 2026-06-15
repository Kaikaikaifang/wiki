---
title: "Vibe-Coding a Dashboard? Here Are 5 Steps So It Doesn't Suck"
source: "https://motherduck.com/blog/vibecoding-dashboards-best-practices/"
author:
  - "[[MotherDuck]]"
published: 2026-04-14
created: 2026-06-15
description: "Five fundamental data visualization principles that transform AI-generated dashboards from pretty charts into actionable insights. Learn chart selection, design, narrative, and interactivity."
tags:
  - "clippings"
---
It's never been easier to build a dashboard. Type a prompt, get JavaScript, and 30 seconds later you've got charts. Congratulations.

But does anyone actually *learn* anything from looking at it? Or do they just go "oh wow" and close the tab?

The difference isn't the tech — it's knowing a few fundamentals about data visualization *before* you hit enter on that prompt. Here are five steps that will make your vibe-coded dashboards actually useful, not just pretty.

I'll show the dos and don'ts with prompting tips along the way. The demo uses Claude and MotherDuck Dive, but these tips apply to any tool where you speak English and get JavaScript charts.

NOTE

If you're interested in the broader picture of BI in the age of AI agents, we built a full guide on that: [Guide to BI in the Agentic Era](https://motherduck.com/lp/guide-to-bi-in-the-agentic-era-full/).

## The Dataset

Our case study is the **WHO Ambient Air Quality Database** — PM2.5, PM10, and NO2 measurements across 7,000+ cities between 2010 and 2022. The measurement is always micrograms per cubic meter (μg/m³), and the higher the number, the worse your air quality.

![Screenshot 2026-04-09 at 17.49.30.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_49_30_3c636c2c33.png&w=3840&q=75)

Quick reference for PM2.5:

- **≤ 5 μg/m³**: Safe (WHO guideline)
- **5–15**: Moderate
- **15–35**: Unhealthy
- **\> 35**: Hazardous

Spoiler: a lot of cities are above the WHO recommendation.

The official source is an Excel sheet (yes, painful), but we've got you covered with a CSV and Parquet file on a public S3 you can use with your favorite data tool. And yes — you should use DuckDB, or at least tell your AI to use DuckDB.

## Step 1: Start With a Question, Not a Chart

This is the classic mistake. You get excited, open your AI tool, and type something like *"show me some data visualizations on this dataset."* And you get... a wall of charts that say nothing.

Instead, answer three questions before you prompt anything:

1. **Who is the audience?** A policy maker needs different views than a journalist or your grandma.
2. **What decision should this inform?** If nobody acts on it, it's just decoration. Put it on your wall as a painting.
3. **What's the one key takeaway?** If everything is highlighted, nothing is.

For our air quality dashboard, the audience is regular people — my grandma, my wife, anyone. And the story is: **is the air getting cleaner in my city? Where and for whom?**

Underneath that: how polluted is my environment, how does it compare regionally, is it getting better or worse, and what can I do about it?

And here's something cool. The question "what can I do about it" — the WHO dataset doesn't actually have that. It tells you *where* things improved, but not *why*. But your LLM probably knows why. Cities in China improved because of the Blue Sky Policy, for example. So let the data show you *who* improved, and the LLM tell you *why*. That's where the real knowledge lives.

## Step 2: Match the Chart Type to the Question Type

Chart types equal question types, not decoration. There are frameworks for this, and you don't have to guess.

![Screenshot 2026-04-09 at 17.50.20.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_50_20_dc7b978753.png&w=3840&q=75)

For our data:

- **Evolution** (is PM2.5 improving?) → Line chart
- **Ranking** (which regions are worst?) → Bar chart
- **Correlation** (PM2.5 vs NO2?) → Scatter plot

One of the best references I know is [**From Data to Viz**](https://www.data-to-viz.com/) by Yan Holtz and Conor Healy. It's a decision tree: what type of data you have, and what you want to show — distribution, ranking, evolution, correlation. Those answers narrow your chart choice to two or three options, and you prompt those *specifically* instead of praying the AI lord guesses it right.

![Screenshot 2026-04-09 at 17.50.47.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_50_47_9fa2f2dd65.png&w=3840&q=75) *From data to viz decision tree*

### Pie vs. Bar: A Classic Example

Let's apply this directly to a classic anti-pattern. Both charts below show average PM2.5 by region. But with a pie chart, it's genuinely hard to tell the difference between angle slices. With a horizontal bar chart, the ranking is instant. Humans are great at comparing lengths, terrible at comparing angles.

![Screenshot 2026-04-09 at 17.55.03.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_55_03_41ab9d5697.png&w=3840&q=75)

**Prompt tip:** Be specific about the chart type. Don't leave it to chance.

> *"Add a horizontal bar chart ranking all world regions by their average PM2.5 concentration (highest to lowest) for the most recent available year, colored by WHO severity tiers (green ≤5, blue ≤15, orange ≤35, red >35) and annotated with a WHO guideline reference line at 5 µg/m³."*

### Anti-Patterns to Avoid

While we're at it — a few chart types that should almost never make it into your dashboard:

- Pie charts with too many categories (like 124 countries — please no)
- 3D anything
- Dual unrelated axes
- Spaghetti charts with 20+ lines

## Step 3: Design With Intention

You've got the right chart type — now don't ruin it with bad design. Four principles.

### Color With Intention

Default AI dashboards use random rainbow colors with no meaning. Instead, use a **severity palette** where colors actually mean something:

- **Green** (#2d7a08): ≤ 5 — WHO safe
- **Blue** (#0777b3): 5–15 — Moderate
- **Orange** (#e18727): 15–35 — Unhealthy
- **Red** (#bc1200): > 35 — Hazardous

Keep it to five colors max. Stay consistent. Pass the hex codes directly in your prompt so the AI doesn't guess. Tools like [ColorBrewer 2.0](https://colorbrewer2.org/) can help you pick a palette if you're not feeling inspired.

### Reduce the Clutter

This comes from Edward Tufte's *The Visual Display of Quantitative Information*. His principle: **maximize the data-ink ratio**. Every pixel on screen should earn its place.

In practice:

- Remove excessive gridlines — keep only horizontal light grey
- Remove chart borders and shadows
- Label directly when possible instead of using a legend
- No background fills on chart areas
![Screenshot 2026-04-09 at 17.58.01.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_58_01_fe8e5fc6df.png&w=3840&q=75)

**Prompt tip:**

> *"Use a minimal, clean design. Remove chart borders and shadows. Light gray gridlines only. No background fills on chart areas."*

You can even mention Tufte by name — the LLM knows who he is.

### Visual Hierarchy

People scan screens in an **F-pattern** — top-left first, then across, then down. Structure your dashboard accordingly:

1. **KPI cards** — headline numbers at the top
2. **Primary chart** — the most important trend (top-left)
3. **Supporting charts** — ranking or comparison (below or beside)
4. **Detail table** — exact numbers for deep dives (bottom)
![Screenshot 2026-04-09 at 17.58.12.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_58_12_b9479a56ae.png&w=3840&q=75)

**Prompt tip:**

> *"Layout: KPI cards in a row at the top, then a line chart showing the global trend, then a bar chart ranking regions, then a table of top improving cities."*

Specify the layout. It's really important so the AI doesn't guess for you.

### Add Context

Numbers without context are meaningless.

- Add **reference lines** (e.g., a dashed WHO safe limit line)
- **Annotate events** (e.g., a vertical line for COVID-19 lockdowns — you'll see a drastic air quality improvement because we were all inside)
- **Always start bar charts at zero** — truncated axes exaggerate differences
- **Include the data source and time period** — always
![Screenshot 2026-04-09 at 17.58.27.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_58_27_03844f75a2.png&w=3840&q=75)

**Prompt tip:**

> *"Add a dashed reference line at PM2.5 = 5 labeled 'WHO Guideline (5 µg/m³)' in red. Annotate 2020 with a vertical dashed line labeled 'COVID-19 lockdowns' in orange."*

### Pick a Theme

Colors, typography, chart rules, general feel — that's your theme. It should be consistent and feel like *your brand*. A few references to try:

- **Tufte Minimal**: Georgia serif, #FFFFFF background, maximum data-ink ratio — nothing decorative
- **Knowledge is Beautiful**: Inspired by David McCandless's book
- **FT Salmon**: The classic Financial Times look

You can pass any of these as a theme directive in your prompt, and the LLM will get it.

![Screenshot 2026-04-09 at 17.58.48.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_58_48_278d2cd017.png&w=3840&q=75)

## Step 4: Build a Narrative Arc

A dashboard should tell a story, not just display numbers. This comes from Cole Nussbaumer Knaflic's [*Storytelling with Data*](https://www.storytellingwithdata.com/). If you read only one data viz book, make it that one.

The narrative arc:

1. **Setup** — what's normal? (8,500+ cities measured worldwide)
2. **Tension** — what's wrong? (93% exceed safe pollution levels)
3. **Insight** — the "aha!" (Some cities cut pollution by 60%+)
4. **Action** — now what? (How does *your* city rank? What can you do?)

For our final dashboard on Paris, that translates to:

- KPI cards showing current concentration (in blue — safe zone, but still 2.9x above the WHO limit)
- A ranking showing how Paris compares to other European cities
- A trend chart showing the trajectory over the years
- Actionable tips on what you can do to improve air quality
![Screenshot 2026-04-09 at 17.59.36.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_59_36_0c9638c1e7.png&w=3840&q=75)

## Step 5: Make It Interactive — But Not Overwhelming

Notice I didn't bring up interactivity until step five. That's intentional. Too many people slap filters everywhere from the start, and it just confuses users. **Start with a static dashboard. Add interactivity only when follow-up questions arise.**

When you do add it:

- **City picker** — search/select specific locations
- **Year toggle** — change the time range
- **Cross-filtering** — click a filter and it applies to all charts (otherwise it gets confusing)
- **Tooltips** — show extra detail on hover

Interactivity should support the narrative, not distract from it.

![Screenshot 2026-04-09 at 17.59.54.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2FScreenshot_2026_04_09_at_17_59_54_785acabfe6.png&w=3840&q=75)

## The Prompt Difference

Here's the thing. Taking these five steps and baking them into your prompt makes a dramatic difference.

**Before (lazy prompt):**

> *"Create some data visualizations from this dataset."*

**After (informed prompt):** Includes the dataset path, narrative arc, specific chart types, hex color codes, layout instructions, reference lines, and interactivity specs.

Same AI. Same data. Night and day results.

## Bonus: Make It a Reusable Skill

You might be thinking: do I really have to type all of this every time? Nope. You can turn these rules into a reusable system prompt or AI skill — a SKILL.md file that encodes the decision tree, blocks anti-patterns (no gradients, no 3D), and enforces design rules (spacing, typography, color palettes).

Even a lazy prompt produces dramatically better results when the skill is loaded.

But here's why I didn't lead with the skill: **the AI follows the rules, it doesn't understand them.** When something looks off — a clipped axis label, mismatched colors, an off-scale chart — you need to be the one who catches it. Dashboards are for humans. The final check has to be human too.

## TL;DR

1. **Define a question** before you touch a chart
2. **Match the chart type** to the question type — use [From Data to Viz](https://www.data-to-viz.com/)
3. **Design with intention** — theme, colors, layout, context lines
4. **Build a narrative** — setup, tension, insight, action
5. **Add interactivity last** — every filter should answer the next "so what?"

TIP

Want to see the final result? [Play with the interactive Dive from this post](https://motherduck.com/dive-gallery/embed/how-to-create-beautiful-dataviz-vibecoding-dashboard/). Looking for more inspiration, or have a great visualization to share? Browse the [Dive Gallery](https://divegallery.motherduck.com/dive-gallery).

## References

- [From Data to Viz](https://www.data-to-viz.com/) — Yan Holtz and Conor Healy
- *The Visual Display of Quantitative Information* — Edward Tufte
- [*Storytelling with Data*](https://www.storytellingwithdata.com/) — Cole Nussbaumer Knaflic
- *Knowledge is Beautiful* — David McCandless
- [ColorBrewer 2.0](https://colorbrewer2.org/) — Color palette tool
- [Guide to BI in the Agentic Era](https://motherduck.com/lp/guide-to-bi-in-the-agentic-era-full/) — MotherDuck

Take care of your dashboards. Next time you vibe-code one, make it useful, not just "wow."