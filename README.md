# 🚀 InstaMedia AI: The Multi-Agent Emotional Signal Engine

**AWS AI for Bharat Hackathon Submission** | [cite_start]**Team Name:** newGPT [cite: 6] | [cite_start]**Team Leader:** Sukhesh kanna Saravanan [cite: 7]
<img width="1470" height="729" alt="Screenshot 2026-03-08 at 11 42 05 PM" src="https://github.com/user-attachments/assets/346df0c1-d39c-43ce-a002-2fc304c60c27" />



[cite_start]Generative AI has completely solved content production speed, but it broke something much more important: **Emotional Connection**[cite: 15]. [cite_start]Currently, 68% of consumers report that AI-generated content feels hollow, leading to a massive drop in trust and engagement[cite: 21, 24, 25]. Furthermore, traditional emotionally-engaging video shoots remain completely unaffordable for local Indian MSMEs. 

[cite_start]**InstaMedia AI** bridges this **Resonance Gap**[cite: 14]. [cite_start]It is not just an AI generator; it is an autonomous digital marketing agency built on a serverless AWS pipeline[cite: 39, 40].

<img width="875" height="475" alt="Screenshot 2026-03-09 at 1 40 56 AM" src="https://github.com/user-attachments/assets/19e145ce-d759-4b74-b017-dddfe79206ad" />

---
<img width="658" height="325" alt="Screenshot 2026-03-09 at 1 41 24 AM" src="https://github.com/user-attachments/assets/36ec4cb3-9f96-4f5e-98b9-463a8d9d5210" />

## 💡 Core Features & Use Cases

1. [cite_start]**Brand DNA Vault**[cite: 30]: Autonomously extracts your Brand DNA from past content. [cite_start]It analyzes color palettes, pacing, and human emotional cues to build a custom vault, ensuring every generated ad intrinsically feels like your brand[cite: 80].
2. [cite_start]**Autonomous Creative Studio** [cite: 81][cite_start]: A multi-agent AI workflow that autonomously handles scriptwriting, storyboarding, voiceover synthesis, and video rendering[cite: 81].
3. [cite_start]**Hyper-Localization at Scale (Bharat-First)**: Dynamically replaces text and lip-syncs voiceovers into multiple Indic languages (Hindi, Tamil, Telugu, Marathi) in real-time[cite: 81, 471, 473].
4. **Predictive A/B Testing via ERS**: Before publishing, our Analyst Agent scores the generated video using a proprietary **Emotional Resonance Score (ERS)**:
   [cite_start]`ERS = log1p(likes * 0.2 + comments * 0.5 + shares * 0.8) * 10`[cite: 106].

---

## ⚙️ System Architecture & Solution Flow

InstaMedia AI operates on an event-driven, multi-agent pipeline designed to deliver enterprise-grade rendering at near-zero idle cost.

### Architecture Flow Diagram

```mermaid
graph TD
    %% User Interaction Layer
    User[👤 User / Editor] -->|Inputs Goals / CSV| UI[💻 React Frontend]
    UI -->|HTTPS Requests| API[Gateway / Flask API]

    %% Intelligence & Memory Layer
    subgraph "Learning Loop & Memory"
        API -->|Uploads Past Ads| S3[(Amazon S3)]
        S3 -->|Analyzes Visuals| Rek[Amazon Rekognition]
        API -->|Calculates ERS| ERS_Calc[ERS Scoring Engine]
        Rek --> Titan[Bedrock: Titan Embeddings]
        ERS_Calc --> Titan
        Titan -->|Stores Vector + ERS| Chroma[(ChromaDB Vector Graph)]
    end

    %% Multi-Agent Orchestration
    subgraph "Agentic Generation (AWS Bedrock & Lambdas)"
        API --> Orch[🧠 Orchestrator Agent]
        Chroma -->|Conditions on Top ERS| Orch
        Orch --> Idea[💡 Ideation Agent]
        Orch --> Studio[🎨 Creative Studio Agent]
        Orch --> Publisher[📅 Publisher Agent]
    end

    %% Rendering & Localization
    subgraph "Real-Time Rendering Muscle"
        Studio --> Polly[Amazon Polly - Indic Voices]
        Studio --> Spot[Amazon EC2 Spot Instances / Worker]
        Spot --> VideoModel[SageMaker / Video Gen Models]
        Polly --> MediaConvert[AWS Elemental MediaConvert]
        VideoModel --> MediaConvert
    end

    %% Validation & Delivery
    MediaConvert -->|Draft Video| Validate[Analyst Agent]
    Validate -->|Assigns Predicted ERS| UI
    UI -->|Human Approves| Publish[Publish to Social APIs]
    Publish -->|New Engagement Data| ERS_Calc

