import os
import datetime
import json
import re
import time
from html import escape
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI


# -----------------------------
# Page & Global Configuration
# -----------------------------

EUROUS_LOGO_URL = "https://eurousventures.com/wp-content/uploads/2024/11/logo_eurousventures_2025_.png"
EUROUS_FAVICON_URL = "https://eurousventures.com/favicon.ico"
BACKGROUND_VIDEO_CANDIDATES = [
]

st.set_page_config(
    page_title="EuroUS Intelligence",
    page_icon=EUROUS_FAVICON_URL,
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_meta_tags() -> None:
    meta_html = """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """
    st.markdown(f"<head>{meta_html}</head>", unsafe_allow_html=True)


def inject_mobile_and_print_css() -> None:
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Oxanium:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --font-display: "Oxanium", "DM Sans", sans-serif;
        --font-body: "DM Sans", -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
        --font-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        --accent-orange: #f17300;

        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.5rem;
        --space-6: 2rem;

        --radius-sm: 0px;
        --radius-md: 0px;
        --radius-lg: 0px;

        --motion-fast: 170ms;
        --motion-base: 260ms;
        --motion-slow: 420ms;
        --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);

        --eurous-blue-1: #054a91;
        --eurous-navy-1: #054a91;
        --eurous-blue-2: #3e7cb1;
        --eurous-blue-3: #054a91;
        --eurous-blue-4: #81a4cd;
        --eurous-bg: #f3f6fb;
        --eurous-card-bg: #FFFFFF;
        --eurous-line: #b7c9de;
        --eurous-line-strong: #81a4cd;
        --eurous-soft: #dbe4ee;
        --eurous-ink-soft: #5c7492;
        --shift-coral: #3e7cb1;
        --shift-charcoal: #054a91;
        --shift-ash: #dbe4ee;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--eurous-bg) !important;
        background-image: none !important;
        color: var(--eurous-navy-1) !important;
        font-family: var(--font-body);
        overflow-y: auto !important;
    }
    [data-testid="stAppViewContainer"] {
        position: relative !important;
    }
    .lineart-stage {
        display: none !important;
    }
    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 920px !important;
        width: min(100%, 920px) !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
    }

    header, footer, [data-testid="stToolbar"], [data-testid="stSidebar"] {
        display: none !important;
    }

    .block-container {
        padding-top: 0.8rem;
        padding-bottom: var(--space-6);
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        max-width: 920px;
        margin: 0 auto;
        background-color: #eef3f9 !important;
        border: 1px solid #c6d6e8;
        border-radius: var(--radius-lg);
        box-shadow: none;
        overflow: visible;
        max-height: none !important;
        animation: pageEnter 700ms var(--ease-out) both;
        position: relative;
        z-index: 1;
        isolation: isolate;
    }
    .block-container::before {
        content: "";
        position: absolute;
        inset: 0;
        background: #eef3f9;
        z-index: -1;
        pointer-events: none;
    }

    .shift-hero {
        display: grid;
        grid-template-columns: 2fr 1fr;
        border-radius: 0;
        overflow: hidden;
        border: 1px solid #b7c9de;
        margin-bottom: 0.45rem;
    }
    .shift-hero-left {
        background: var(--shift-coral);
        color: #f3f8ff;
        padding: 0.7rem 0.9rem 0.75rem 0.9rem;
        min-height: 156px;
        position: relative;
    }
    .shift-logo-mini {
        width: 156px;
        max-width: 45%;
        display: block;
        margin-bottom: 0.5rem;
        filter: saturate(0.92) contrast(1.04) brightness(1.08);
    }
    .shift-hero-kicker {
        font-family: var(--font-display);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.62rem;
        opacity: 0.86;
        margin-bottom: 0.45rem;
    }
    .shift-hero-title {
        font-family: var(--font-display);
        font-size: clamp(2.3rem, 7.6vw, 5.35rem);
        line-height: 0.88;
        letter-spacing: -0.045em;
        font-weight: 700;
        margin: 0;
        max-width: 98%;
        text-transform: uppercase;
    }
    .shift-hero-subline {
        margin-top: 0.42rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: rgba(236, 243, 255, 0.94);
    }

    .shift-hero-right {
        background: var(--shift-ash);
        color: #15233F;
        border-left: 1px solid rgba(129, 164, 205, 0.45);
        display: flex;
        flex-direction: column;
    }
    .shift-hero-right-copy {
        padding: 0.72rem 0.78rem 0.66rem 0.78rem;
        font-size: 0.86rem;
        line-height: 1.2;
        font-weight: 600;
        border-bottom: 1px solid rgba(129, 164, 205, 0.45);
    }
    .shift-hero-right-status {
        background: var(--shift-charcoal);
        color: #E6EAF4;
        padding: 0.68rem 0.72rem 0.72rem 0.72rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.44rem;
        position: relative;
        overflow: hidden;
    }
    .shift-hero-right-status::after {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: -45%;
        width: 42%;
        pointer-events: none;
        background: linear-gradient(
            90deg,
            rgba(143, 179, 255, 0) 0%,
            rgba(143, 179, 255, 0.08) 45%,
            rgba(143, 179, 255, 0.18) 50%,
            rgba(143, 179, 255, 0.08) 55%,
            rgba(143, 179, 255, 0) 100%
        );
        animation: telemetrySweep 2200ms var(--ease-out) 1 760ms both;
    }
    .shift-hero-right-status .status-strip {
        border: 1px solid rgba(222, 230, 246, 0.2);
        background: rgba(255, 255, 255, 0.03);
        color: #B9C4DD;
        padding: 0.25rem 0.42rem;
    }
    .shift-hero-right-status .status-label {
        color: #9FB0D3;
    }
    .shift-hero-right-status .status-online {
        color: var(--accent-orange);
    }
    .shift-hero-right-status .status-refresh {
        color: #B6BCC8;
    }
    .shift-hero-right-status .status-dot {
        background: #8CA0CC;
    }
    .system-telemetry {
        border-top: 1px solid rgba(177, 192, 222, 0.22);
        padding-top: 0.5rem;
        font-family: var(--font-mono);
        color: #C8D4F0;
    }
    .system-telemetry-title {
        font-size: 0.63rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #95A8D7;
        margin-bottom: 0.38rem;
    }
    .system-telemetry-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.45rem;
        font-size: 0.67rem;
        line-height: 1.28;
        margin-bottom: 0.22rem;
        opacity: 1;
        transform: translateX(0);
        animation: telemetryIn 440ms var(--ease-out) forwards;
    }
    .system-telemetry-row:last-child {
        margin-bottom: 0;
    }
    .system-telemetry-row:nth-child(2) { animation-delay: 120ms; }
    .system-telemetry-row:nth-child(3) { animation-delay: 200ms; }
    .system-telemetry-row:nth-child(4) { animation-delay: 280ms; }
    .system-telemetry-row:nth-child(5) { animation-delay: 360ms; }
    .system-telemetry-name {
        color: #DCE6FF;
    }
    .system-telemetry-val {
        color: #81a4cd;
    }

    .controls-row {
        margin-top: 0.34rem;
        margin-bottom: 0.44rem;
    }

    .control-divider {
        border-top: 1px solid #b7c9de;
        margin: 0.34rem 0 0.44rem 0;
    }

    .stButton > button {
        min-height: 48px !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-family: var(--font-display) !important;
        letter-spacing: 0.024em;
        text-transform: uppercase;
        background-color: var(--shift-charcoal) !important;
        color: white !important;
        border: none !important;
        transition: transform var(--motion-fast) var(--ease-out), background-color var(--motion-base) var(--ease-out), box-shadow var(--motion-base) var(--ease-out);
        position: relative;
        overflow: hidden;
        box-shadow: none;
    }
    .stButton > button,
    .stButton > button span,
    .stButton > button p,
    .stButton > button div {
        color: #EEF4FF !important;
        -webkit-text-fill-color: #EEF4FF !important;
    }
    .stDownloadButton > button,
    .stDownloadButton > button span,
    .stDownloadButton > button p,
    .stDownloadButton > button div {
        color: #EEF4FF !important;
        -webkit-text-fill-color: #EEF4FF !important;
    }
    .stDownloadButton > button {
        background-color: #054a91 !important;
        border: 1px solid #3e7cb1 !important;
    }
    .stButton > button:disabled,
    .stButton > button:disabled span,
    .stButton > button:disabled p,
    .stButton > button:disabled div {
        color: #AFC0E8 !important;
        -webkit-text-fill-color: #AFC0E8 !important;
        opacity: 1 !important;
    }
    .stDownloadButton > button:disabled,
    .stDownloadButton > button:disabled span,
    .stDownloadButton > button:disabled p,
    .stDownloadButton > button:disabled div {
        color: #AFC0E8 !important;
        -webkit-text-fill-color: #AFC0E8 !important;
        opacity: 1 !important;
    }
    .stButton > button::after {
        content: "";
        position: absolute;
        top: 0;
        left: -120%;
        width: 65%;
        height: 100%;
        background: linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.35) 50%, rgba(255,255,255,0) 100%);
        transform: skewX(-20deg);
    }
    .stButton > button:hover::after {
        animation: buttonSheen 900ms ease-out forwards;
    }
    .stButton > button:active {
        transform: scale(0.98);
        background-color: #0D111B !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: none;
    }
    .stDownloadButton > button:hover,
    .stDownloadButton > button:active,
    .stDownloadButton > button:focus {
        background-color: #09316c !important;
        border-color: #3e7cb1 !important;
        color: #EEF4FF !important;
        -webkit-text-fill-color: #EEF4FF !important;
    }

    .stTextInput > div > div > input {
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-family: var(--font-display) !important;
        letter-spacing: 0.01em;
        border: 1px solid #3e7cb1 !important;
        background-color: #FFFFFF !important;
        color: #054a91 !important;
        -webkit-text-fill-color: #054a91 !important;
        caret-color: #054a91 !important;
        transition: border-color var(--motion-fast) var(--ease-out), box-shadow var(--motion-fast) var(--ease-out), transform var(--motion-fast) var(--ease-out);
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--shift-charcoal) !important;
        box-shadow: 0 0 0 3px rgba(19, 22, 32, 0.12);
        transform: translateY(-1px);
    }
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div,
    [data-testid="stTextInput"] input {
        border-radius: 0 !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #8B8C90 !important;
        opacity: 1 !important;
        font-family: var(--font-display) !important;
        letter-spacing: 0.01em;
    }

    h1, h2, h3, .eurous-title, .eurous-subtitle {
        font-family: var(--font-display) !important;
        letter-spacing: 0.01em;
    }

    .eurous-logo-wrap {
        width: 100%;
        margin-top: 0.1rem;
        margin-bottom: 0.7rem;
    }
    .eurous-logo {
        width: 180px;
        max-width: 56vw;
        display: block;
        margin-left: auto;
        margin-right: 0;
    }

    .topbar {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 0.8rem;
        margin-bottom: 0.2rem;
    }
    .topbar-spacer {
        min-height: 24px;
        flex: 1;
    }

    .smart-briefs-title {
        text-align: center;
        margin-top: 1.15rem;
        margin-bottom: 0.35rem;
        font-family: "Oxanium", "DM Sans", sans-serif;
        font-weight: 700;
        font-size: 1.45rem;
        color: #054a91;
    }
    .status-strip {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.2rem;
        margin-top: 0;
        margin-bottom: 0;
        color: var(--eurous-ink-soft);
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-family: var(--font-display);
        background: linear-gradient(180deg, rgba(255,255,255,0.78), rgba(255,255,255,0.56));
        border: 1px solid var(--eurous-line);
        border-radius: 0;
        padding: 0.25rem 0.5rem;
        backdrop-filter: blur(2px);
    }
    .status-label {
        color: #89898C;
    }
    .status-state {
        position: relative;
        display: inline-block;
        min-width: 4.3rem; /* keeps dots from sitting on top of ONLINE */
        height: 1.05rem;
        text-align: left;
    }
    .status-online {
        color: var(--accent-orange);
        font-weight: 700;
        position: relative;
        left: 0;
        top: 0;
        white-space: nowrap;
        animation: statusOnlineFade 120s linear forwards;
    }
    .status-refresh {
        color: #81a4cd;
        font-weight: 700;
        position: absolute;
        left: 0;
        top: 0;
        white-space: nowrap;
        opacity: 0;
        animation: statusRefreshShow 120s linear forwards;
    }
    .status-dots {
        display: inline-flex;
        gap: 0.22rem;
        margin-left: 0.12rem;
    }
    .status-dot {
        width: 0.32rem;
        height: 0.32rem;
        border-radius: 999px;
        background: #81a4cd;
        animation: statusPulse 1.2s ease-in-out 8 both;
    }
    .status-dot:nth-child(2) { animation-delay: 0.16s; }
    .status-dot:nth-child(3) { animation-delay: 0.32s; }
    .status-dot:nth-child(4) { animation-delay: 0.48s; }
    .status-dot:nth-child(5) { animation-delay: 0.64s; }

    .reliability-badge-wrap {
        display: flex;
        justify-content: flex-start;
        margin-top: 0.22rem;
    }
    .reliability-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 0;
        border: 1px solid;
        padding: 0.13rem 0.45rem;
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 0.66rem;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        line-height: 1.1;
    }
    .reliability-badge.strict {
        color: #054a91;
        background: #e9f1f8;
        border-color: #81a4cd;
    }
    .reliability-badge.balanced {
        color: #3e7cb1;
        background: #eef3f9;
        border-color: #81a4cd;
    }

    .typewriter-wrap {
        margin-top: 0.25rem;
        margin-bottom: 0.05rem;
        min-height: 1rem;
    }

    [data-testid="stToggle"] {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-top: 0.22rem;
        margin-bottom: 0;
        width: 100%;
    }
    [data-testid="stToggle"] label p {
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        color: #054a91 !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        font-size: 0.78rem !important;
    }
    [data-testid="stToggle"] [role="switch"] {
        isolation: isolate;
        position: relative;
        width: 60px !important;
        min-width: 60px !important;
        height: 30px !important;
        border-radius: 15px !important;
        border: none !important;
        overflow: hidden !important;
        background: #ecf0f3 !important;
        box-shadow:
            -8px -4px 8px 0px #ffffff,
            8px 4px 12px 0px #d1d9e6,
            4px 4px 4px 0px #d1d9e6 inset,
            -4px -4px 4px 0px #ffffff inset !important;
        opacity: 1 !important;
        filter: none !important;
        transform: none !important;
        transition: background 0.4s cubic-bezier(0.85, 0.05, 0.18, 1.35), box-shadow 0.35s ease !important;
    }
    [data-testid="stToggle"] [role="switch"][aria-checked="true"] {
        background: #dbe4ee !important;
        opacity: 1 !important;
    }
    [data-testid="stToggle"] [role="switch"] > div {
        width: 30px !important;
        height: 30px !important;
        border-radius: 15px !important;
        margin: 0 !important;
        background: #ecf0f3 !important;
        border: none !important;
        box-shadow:
            -8px -4px 8px 0px #ffffff,
            8px 4px 12px 0px #d1d9e6 !important;
        transition: transform 0.4s cubic-bezier(0.85, 0.05, 0.18, 1.35), background 0.3s ease !important;
    }
    [data-testid="stToggle"] [role="switch"][aria-checked="true"] > div {
        transform: translateX(30px) !important;
        background: #3e7cb1 !important;
    }
    [data-testid="stToggle"] input {
        opacity: 1 !important;
    }
    /* Hard override: draw neumorphic toggle via pseudo-element. */
    [data-testid="stToggle"] button[role="switch"] {
        position: relative !important;
        width: 60px !important;
        min-width: 60px !important;
        height: 30px !important;
        border-radius: 15px !important;
        border: none !important;
        background: #ecf0f3 !important;
        box-shadow:
            -8px -4px 8px 0px #ffffff,
            8px 4px 12px 0px #d1d9e6,
            4px 4px 4px 0px #d1d9e6 inset,
            -4px -4px 4px 0px #ffffff inset !important;
        overflow: hidden !important;
    }
    [data-testid="stToggle"] button[role="switch"] > * {
        opacity: 0 !important;
    }
    [data-testid="stToggle"] button[role="switch"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: -45%;
        width: 200%;
        height: 100%;
        background: #ecf0f3;
        border-radius: 15px;
        transform: translate3d(-30%, 0, 0);
        transition: transform 0.4s cubic-bezier(0.85, 0.05, 0.18, 1.35);
        box-shadow: -8px -4px 8px 0px #ffffff, 8px 4px 12px 0px #d1d9e6;
    }
    [data-testid="stToggle"] button[role="switch"][aria-checked="true"]::before {
        transform: translate3d(18%, 0, 0);
        background: #3e7cb1;
    }
    .typewriter-text {
        display: inline-block;
        max-width: 100%;
        color: #054a91;
        font-size: 0.98rem;
        white-space: nowrap;
        overflow: hidden;
        border-right: 1px solid #3e7cb1;
        width: 0;
        opacity: 0;
        padding-right: 0.08rem;
        animation: typeShow 0.01s linear 1.2s forwards, typing 2s steps(40, end) 1.2s forwards, caretBlink 0.7s step-end 1.2s 3, caretHide 0.01s linear 3.2s forwards;
    }

    .scorecard-heading {
        font-family: "Oxanium", "DM Sans", sans-serif;
        font-size: 1.12rem;
        font-weight: 700;
        color: #054a91;
        margin: 0.6rem 0 0.35rem 0;
    }
    .scorecard-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.55rem;
        margin: 0.35rem 0 0.8rem 0;
    }
    @media (min-width: 620px) {
        .scorecard-grid { grid-template-columns: 1fr 1fr; }
    }
    .scorecard-card {
        background: #FFFFFF;
        border: 1px solid var(--eurous-line);
        border-radius: var(--radius-md);
        padding: 0.62rem 0.72rem;
        box-shadow: none;
        transition: border-color var(--motion-base) var(--ease-out), box-shadow var(--motion-base) var(--ease-out), transform var(--motion-base) var(--ease-out);
        position: relative;
        overflow: hidden;
        animation: cardIn 600ms var(--ease-out) both;
    }
    .scorecard-card:nth-child(2) { animation-delay: 80ms; }
    .scorecard-card:nth-child(3) { animation-delay: 140ms; }
    .scorecard-card:nth-child(4) { animation-delay: 200ms; }
    .scorecard-card:nth-child(5) { animation-delay: 260ms; }
    .scorecard-card:nth-child(6) { animation-delay: 320ms; }
    .scorecard-card::before {
        content: "";
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(180deg, rgba(52,112,116,0) 0px, rgba(52,112,116,0) 5px, rgba(52,112,116,0.07) 6px);
        opacity: 0.28;
        pointer-events: none;
    }
    .scorecard-card:hover {
        border-color: var(--eurous-line-strong);
        box-shadow: none;
        transform: translateY(-2px);
    }
    .scorecard-axis {
        font-family: "Oxanium", "DM Sans", sans-serif;
        letter-spacing: 0.02em;
        color: #89898C;
        font-size: 0.76rem;
        margin-bottom: 0.22rem;
        text-transform: uppercase;
    }
    .scorecard-line {
        font-size: 0.95rem;
        font-weight: 700;
        color: #054a91;
        margin-bottom: 0.18rem;
    }
    .scorecard-dots {
        color: #054a91;
        letter-spacing: 0.08rem;
        font-size: 0.82rem;
        margin-left: 0.22rem;
    }
    .scorecard-tag {
        color: #054a91;
        font-size: 0.84rem;
        font-weight: 600;
    }

    .stMarkdown h1 {
        font-size: clamp(1.85rem, 5.1vw, 2.85rem);
        line-height: 0.95;
        letter-spacing: -0.035em;
        text-transform: uppercase;
        border-bottom: 1px solid #D7DFEC;
        padding-bottom: 0.5rem;
        margin-bottom: 0.95rem;
    }
    .stMarkdown h2 {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 1.4rem;
        margin-bottom: 0.5rem;
        color: var(--eurous-blue-3);
    }
    .stMarkdown p,
    .stMarkdown li,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        font-size: 0.96rem;
        line-height: 1.42;
        color: #1A2338;
    }
    .stMarkdown ul {
        margin-top: 0.3rem;
        margin-bottom: 0.55rem;
    }

    [data-baseweb="select"] > div {
        min-height: 48px !important;
        background: #054a91 !important;
        border: 1px solid #3e7cb1 !important;
        border-radius: 0 !important;
        color: #EAF0FF !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="select"] div {
        color: #EAF0FF !important;
        font-family: var(--font-display) !important;
        letter-spacing: 0.018em;
        font-size: 0.96rem !important;
    }
    [data-baseweb="select"] svg {
        fill: #EAF0FF !important;
    }
    [data-testid="stTextInput"] {
        margin-top: 0.1rem;
        margin-bottom: 0.38rem;
    }

    .stMarkdown code, [data-testid="stMarkdownContainer"] code {
        background: linear-gradient(90deg, rgba(39, 69, 143, 0.14), rgba(28, 63, 141, 0.08));
        color: #054a91;
        border: 1px solid #CBD8F0;
        border-radius: 0;
        padding: 0.05rem 0.28rem;
        font-family: var(--font-mono);
        font-size: 0.94em;
    }

    [data-testid="stMarkdownContainer"] h2 {
        position: relative;
        padding-left: 0.52rem;
    }
    [data-testid="stMarkdownContainer"] h2::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0.2rem;
        bottom: 0.2rem;
        width: 2px;
        background: linear-gradient(180deg, var(--eurous-blue-1), rgba(28, 63, 141, 0.35));
        border-radius: 2px;
    }

    .stMarkdown ul li {
        margin-bottom: 0.22rem;
        animation: listIn 420ms var(--ease-out) both;
    }

    @keyframes typeShow { to { opacity: 1; } }
    @keyframes typing { from { width: 0; } to { width: 27ch; } }
    @keyframes caretBlink { 50% { border-color: transparent; } }
    @keyframes caretHide { to { border-right-color: transparent; } }
    @keyframes pageEnter {
        from { opacity: 0; transform: translateY(10px) scale(0.995); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes cardIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes listIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes telemetryIn {
        from { opacity: 0; transform: translateX(6px); filter: blur(0.4px); }
        to { opacity: 1; transform: translateX(0); filter: blur(0); }
    }
    @keyframes telemetrySweep {
        from { left: -45%; opacity: 0; }
        8% { opacity: 1; }
        92% { opacity: 1; }
        to { left: 118%; opacity: 0; }
    }
    @keyframes loader_5191 {
        from { opacity: 0.22; }
        to { opacity: 1; }
    }
    .brief-loader-wrap {
        position: relative;
        width: 28px;
        height: 28px;
        margin: 0.15rem auto 0.35rem auto;
    }
    .brief-loader-wrap .square {
        width: 5px;
        height: 5px;
        position: absolute;
        top: 50%;
        left: 50%;
        margin-top: -2.5px;
        margin-left: -2.5px;
        background: #3e7cb1;
    }
    .brief-loader-wrap .sq1 { margin-top: -12.5px; margin-left: -12.5px; animation: loader_5191 675ms ease-in-out 0ms infinite alternate; }
    .brief-loader-wrap .sq2 { margin-top: -12.5px; animation: loader_5191 675ms ease-in-out 75ms infinite alternate; }
    .brief-loader-wrap .sq3 { margin-top: -12.5px; margin-left: 7.5px; animation: loader_5191 675ms ease-in-out 150ms infinite alternate; }
    .brief-loader-wrap .sq4 { margin-left: -12.5px; animation: loader_5191 675ms ease-in-out 225ms infinite alternate; }
    .brief-loader-wrap .sq5 { animation: loader_5191 675ms ease-in-out 300ms infinite alternate; }
    .brief-loader-wrap .sq6 { margin-left: 7.5px; animation: loader_5191 675ms ease-in-out 375ms infinite alternate; }
    .brief-loader-wrap .sq7 { margin-top: 7.5px; margin-left: -12.5px; animation: loader_5191 675ms ease-in-out 450ms infinite alternate; }
    .brief-loader-wrap .sq8 { margin-top: 7.5px; animation: loader_5191 675ms ease-in-out 525ms infinite alternate; }
    .brief-loader-wrap .sq9 { margin-top: 7.5px; margin-left: 7.5px; animation: loader_5191 675ms ease-in-out 600ms infinite alternate; }
    @keyframes statusPulse {
        0%, 100% { transform: scale(0.9); opacity: 0.45; background: #A9BCE3; }
        50% { transform: scale(1.15); opacity: 1; background: #3e7cb1; }
    }
    @keyframes statusOnlineFade {
        0%, 99% { opacity: 1; }
        100% { opacity: 0; }
    }
    @keyframes statusRefreshShow {
        0%, 99% { opacity: 0; }
        100% { opacity: 1; }
    }
    @keyframes buttonSheen { from { left: -120%; } to { left: 130%; } }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
            scroll-behavior: auto !important;
        }
    }

    /* FINAL toggle override: direct switch-button rendering */
    [data-testid="stToggle"] button[role="switch"] {
        position: relative !important;
        width: 60px !important;
        min-width: 60px !important;
        height: 30px !important;
        border-radius: 15px !important;
        border: none !important;
        background: #ecf0f3 !important;
        box-shadow:
            -8px -4px 8px 0 #ffffff,
            8px 4px 12px 0 #d1d9e6,
            4px 4px 4px 0 #d1d9e6 inset,
            -4px -4px 4px 0 #ffffff inset !important;
        overflow: hidden !important;
        padding: 0 !important;
    }
    [data-testid="stToggle"] button[role="switch"] > * {
        display: none !important;
    }
    [data-testid="stToggle"] button[role="switch"]::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 15px;
        background: #ecf0f3;
    }
    [data-testid="stToggle"] button[role="switch"]::after {
        content: "";
        position: absolute;
        top: 2px;
        left: 2px;
        width: 26px;
        height: 26px;
        border-radius: 13px;
        background: #054a91;
        box-shadow: inset 0 0 0.12em #dbe4ee;
        transition: left 0.28s cubic-bezier(0.85, 0.05, 0.18, 1.35) !important;
    }
    [data-testid="stToggle"] button[role="switch"][aria-checked="true"]::before {
        background: #3e7cb1;
    }
    [data-testid="stToggle"] button[role="switch"][aria-checked="true"]::after {
        left: 32px;
        background: #f17300;
    }

    @media print {
        button, input, textarea, select, [data-testid="stSidebar"], [data-testid="stToolbar"], header, footer, .stAlert, .stSpinner, [data-testid="stFeedback"] {
            display: none !important;
        }
        body { background: #ffffff !important; }
        .block-container { margin: 0 !important; padding: 0 !important; max-width: 100% !important; border: none !important; box-shadow: none !important; }
        @page { size: A4; margin: 0.5in; }
    }

    @media (max-width: 920px) {
        .shift-hero {
            grid-template-columns: 1fr;
        }
        .shift-hero-right {
            border-left: none;
            border-top: 1px solid rgba(17, 21, 33, 0.14);
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def inject_motion_mode_css() -> None:
    """
    Runtime motion intensity override controlled by header selector.
    """
    mode = st.session_state.get("motion_mode", "Subtle")
    if mode == "Off":
        st.markdown(
            """
            <style>
            *, *::before, *::after {
                animation: none !important;
                transition: none !important;
                scroll-behavior: auto !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        return

    if mode == "Medium":
        st.markdown(
            """
            <style>
            :root {
                --motion-fast: 240ms;
                --motion-base: 360ms;
                --motion-slow: 560ms;
            }
            .block-container { animation-duration: 900ms !important; }
            .scorecard-card { animation-duration: 760ms !important; }
            .system-telemetry-row { animation-duration: 620ms !important; }
            .status-dot { animation-iteration-count: 12 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def inject_print_preview_css() -> None:
    """
    On-screen print preview polish before native browser print/save.
    """
    if not st.session_state.get("print_preview_mode", False):
        return
    st.markdown(
        """
        <style>
        .shift-hero-right-status,
        .controls-row,
        .reliability-badge-wrap,
        [data-testid="stToggle"],
        [data-baseweb="select"] {
            display: none !important;
        }
        .block-container {
            max-width: 920px !important;
            border-color: #D1D7E2 !important;
            background: #FFFFFF !important;
        }
        .stMarkdown h1 { font-size: 2rem !important; }
        .stMarkdown h2 {
            margin-top: 1.2rem !important;
            margin-bottom: 0.35rem !important;
            letter-spacing: 0.08em !important;
        }
        .stMarkdown p, .stMarkdown li {
            font-size: 0.94rem !important;
            line-height: 1.36 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_dark_mode_css() -> None:
    """Optional dark mode overrides controlled by header toggle."""
    if not st.session_state.get("dark_mode", False):
        return

    st.markdown(
        """
        <style>
        :root {
            --dm-1: #020969;
            --dm-2: #09316c;
            --dm-3: #10596f;
            --dm-4: #188273;
            --dm-5: #1faa76;
            --dm-6: #26d279;
            --dm-7: #2dfa7c;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background: transparent !important;
            color: #EFFFF6 !important;
        }
        .lineart-stage {
            display: none !important;
        }
        .block-container {
            background: linear-gradient(180deg, #020969, #09316c) !important;
            border-color: rgba(38, 210, 121, 0.42) !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.42) !important;
        }
        .block-container::before {
            background: linear-gradient(180deg, #020969, #09316c) !important;
        }
        .shift-hero {
            border-color: rgba(38, 210, 121, 0.42) !important;
        }
        .shift-hero-left {
            background: linear-gradient(180deg, #10596f, #09316c) !important;
            color: #F4FFF9 !important;
        }
        .shift-hero-title {
            color: #F4FFF9 !important;
        }
        .shift-hero-subline {
            color: #D8FEEB !important;
        }
        .shift-hero-right {
            background: #09316c !important;
            color: #EFFFF6 !important;
            border-left-color: rgba(38, 210, 121, 0.45) !important;
        }
        .shift-hero-right-copy {
            background: #10596f !important;
            color: #EFFFF6 !important;
            border-bottom-color: rgba(38, 210, 121, 0.45) !important;
        }
        .shift-hero-right-status {
            background: #020969 !important;
        }
        .shift-hero-right-status .status-strip {
            border-color: rgba(38, 210, 121, 0.42) !important;
            background: #09316c !important;
            color: #D8FEEB !important;
        }
        .shift-hero-right-status .status-label {
            color: #9FE8C5 !important;
        }
        .shift-hero-right-status .status-online {
            color: #2dfa7c !important;
        }
        .shift-hero-right-status .status-refresh {
            color: #81a4cd !important;
        }
        .shift-hero-right-status .status-dot {
            background: #26d279 !important;
        }
        .system-telemetry {
            border-top-color: rgba(38, 210, 121, 0.42) !important;
            color: #D8FEEB !important;
        }
        .stMarkdown,
        [data-testid="stMarkdownContainer"] {
            color: #EFFFF6 !important;
        }
        .stMarkdown p,
        .stMarkdown li,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            color: #D8FEEB !important;
        }
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {
            color: #F4FFF9 !important;
            border-color: rgba(38, 210, 121, 0.55) !important;
        }
        .stMarkdown a,
        [data-testid="stMarkdownContainer"] a {
            color: #2dfa7c !important;
        }
        .scorecard-card {
            background: linear-gradient(180deg, #09316c, #10596f) !important;
            border-color: rgba(31, 170, 118, 0.55) !important;
        }
        .scorecard-axis, .scorecard-tag, .typewriter-text, .status-strip, .smart-briefs-title {
            color: #D8FEEB !important;
        }
        .scorecard-line,
        .scorecard-dots {
            color: #2dfa7c !important;
        }
        .reliability-badge.strict {
            color: #062D22 !important;
            background: #2dfa7c !important;
            border-color: #2dfa7c !important;
        }
        .reliability-badge.balanced {
            color: #D8FEEB !important;
            background: rgba(24, 130, 115, 0.55) !important;
            border-color: #1faa76 !important;
        }
        .stTextInput > div > div > input {
            background-color: #09316c !important;
            color: #F4FFF9 !important;
            -webkit-text-fill-color: #F4FFF9 !important;
            border-color: #1faa76 !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: #9FE8C5 !important;
            -webkit-text-fill-color: #9FE8C5 !important;
            opacity: 1 !important;
        }
        [data-baseweb="select"] > div {
            background: #09316c !important;
            border-color: #1faa76 !important;
            color: #EFFFF6 !important;
        }
        [data-baseweb="select"] span,
        [data-baseweb="select"] div,
        [data-baseweb="select"] svg {
            color: #EFFFF6 !important;
            fill: #EFFFF6 !important;
        }
        [data-testid="stToggle"] label p {
            color: #D8FEEB !important;
            font-family: var(--font-display) !important;
            font-weight: 700 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
        }
        [data-testid="stToggle"] [role="switch"] {
            background: #09316c !important;
            box-shadow:
                -8px -4px 8px 0px rgba(24, 130, 115, 0.22),
                8px 4px 12px 0px rgba(2, 9, 105, 0.75),
                4px 4px 4px 0px rgba(2, 9, 105, 0.58) inset,
                -4px -4px 4px 0px rgba(38, 210, 121, 0.14) inset !important;
        }
        [data-testid="stToggle"] [role="switch"][aria-checked="true"] {
            background: #10596f !important;
        }
        [data-testid="stToggle"] [role="switch"] > div {
            background: #020969 !important;
            border: none !important;
            box-shadow:
                -8px -4px 8px 0px rgba(24, 130, 115, 0.25),
                8px 4px 12px 0px rgba(2, 9, 105, 0.72) !important;
        }
        [data-testid="stToggle"] [role="switch"][aria-checked="true"] > div {
            background: #2dfa7c !important;
        }
        [data-testid="stToggle"] button[role="switch"] {
            background: #09316c !important;
            box-shadow:
                -8px -4px 8px 0px rgba(24, 130, 115, 0.22),
                8px 4px 12px 0px rgba(2, 9, 105, 0.75),
                4px 4px 4px 0px rgba(2, 9, 105, 0.58) inset,
                -4px -4px 4px 0px rgba(38, 210, 121, 0.14) inset !important;
        }
        [data-testid="stToggle"] button[role="switch"]::before {
            background: #09316c !important;
            box-shadow:
                -8px -4px 8px 0px rgba(24, 130, 115, 0.25),
                8px 4px 12px 0px rgba(2, 9, 105, 0.72) !important;
        }
        [data-testid="stToggle"] button[role="switch"][aria-checked="true"]::before {
            background: #2dfa7c !important;
        }
        .stButton > button {
            background: linear-gradient(180deg, #1faa76, #188273) !important;
            border: 1px solid #26d279 !important;
        }
        .stButton > button,
        .stButton > button span,
        .stButton > button p,
        .stButton > button div {
            color: #031C14 !important;
            -webkit-text-fill-color: #031C14 !important;
        }
        /* FINAL dark-mode override for custom toggle shape */
        [data-testid="stToggle"] button[role="switch"] {
            background: #09316c !important;
            box-shadow:
                -8px -4px 8px 0 rgba(24, 130, 115, 0.22),
                8px 4px 12px 0 rgba(2, 9, 105, 0.75),
                4px 4px 4px 0 rgba(2, 9, 105, 0.58) inset,
                -4px -4px 4px 0 rgba(38, 210, 121, 0.14) inset !important;
        }
        [data-testid="stToggle"] button[role="switch"]::before {
            background: #09316c !important;
        }
        [data-testid="stToggle"] button[role="switch"]::after {
            background: #020969 !important;
            box-shadow: inset 0 0 0.12em #d8feeb !important;
        }
        [data-testid="stToggle"] button[role="switch"][aria-checked="true"]::before {
            background: #188273 !important;
        }
        [data-testid="stToggle"] button[role="switch"][aria-checked="true"]::after {
            background: #2dfa7c !important;
        }
        .stDownloadButton > button,
        .stDownloadButton > button span,
        .stDownloadButton > button p,
        .stDownloadButton > button div {
            color: #031C14 !important;
            -webkit-text-fill-color: #031C14 !important;
        }
        .stDownloadButton > button {
            background: linear-gradient(180deg, #1faa76, #188273) !important;
            border: 1px solid #26d279 !important;
        }
        .stDownloadButton > button:hover,
        .stDownloadButton > button:active,
        .stDownloadButton > button:focus {
            background: linear-gradient(180deg, #26d279, #1faa76) !important;
            border-color: #2dfa7c !important;
            color: #031C14 !important;
            -webkit-text-fill-color: #031C14 !important;
        }
        .system-telemetry-title {
            color: #9FE8C5 !important;
        }
        .system-telemetry-name {
            color: #D8FEEB !important;
        }
        .system-telemetry-val {
            color: #2dfa7c !important;
        }
        .control-divider {
            border-top-color: rgba(38, 210, 121, 0.42) !important;
        }
        .stMarkdown code, [data-testid="stMarkdownContainer"] code {
            background: linear-gradient(90deg, rgba(24, 130, 115, 0.28), rgba(31, 170, 118, 0.22)) !important;
            color: #EFFFF6 !important;
            border-color: rgba(38, 210, 121, 0.55) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Search & LLM Utilities
# -----------------------------

def normalize_url_candidate(raw_url: str) -> str | None:
    token = (raw_url or "").strip().strip("()[]<>{},;\"'")
    if not token:
        return None
    if not re.match(r"^https?://", token, flags=re.IGNORECASE):
        token = f"https://{token}"
    try:
        parsed = urlparse(token)
        if not parsed.netloc or "." not in parsed.netloc:
            return None
        clean_netloc = parsed.netloc.lower()
        clean_path = parsed.path or ""
        normalized = f"{parsed.scheme.lower()}://{clean_netloc}{clean_path}"
        return normalized.rstrip("/")
    except Exception:
        return None


def infer_startup_name_from_domain(domain: str) -> str:
    host = (domain or "").lower().strip()
    if host.startswith("www."):
        host = host[4:]
    parts = [p for p in host.split(".") if p]
    if not parts:
        return "Startup"

    # Handle common multi-part public suffixes (e.g., co.uk).
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net", "gov", "ac"} and len(parts[-1]) <= 3:
        root = parts[-3]
    elif len(parts) >= 2:
        root = parts[-2]
    else:
        root = parts[0]
    name = re.sub(r"[^a-z0-9]+", " ", root).strip()
    return name.title() if name else "Startup"


def parse_startup_input(user_input: str) -> tuple[str, str | None]:
    raw = (user_input or "").strip()
    if not raw:
        return "", None

    url_match = re.search(
        r"((?:https?://)?(?:www\.)?[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?:/[^\s]*)?)",
        raw,
    )
    if not url_match:
        return raw, None

    raw_url = url_match.group(1)
    normalized_url = normalize_url_candidate(raw_url)
    if not normalized_url:
        return raw, None

    parsed = urlparse(normalized_url)
    inferred_name = infer_startup_name_from_domain(parsed.netloc)

    # If user typed both name and URL, prefer explicit name.
    name_without_url = raw.replace(raw_url, " ")
    name_without_url = re.sub(r"[\|\-,;/]+", " ", name_without_url)
    name_without_url = re.sub(r"\s+", " ", name_without_url).strip()
    if any(ch.isalpha() for ch in name_without_url) and len(name_without_url) >= 2:
        return name_without_url, normalized_url
    return inferred_name, normalized_url


def search_duckduckgo(query: str, max_results: int = 30, preferred_url: str | None = None) -> List[Dict[str, Any]]:
    legal_suffixes = {
        "sa", "ag", "inc", "llc", "ltd", "gmbh", "sarl", "bv", "nv", "oy", "ab", "spa", "plc", "corp", "co"
    }

    query_clean = (query or "").strip()
    core_query = re.sub(
        r"\b(?:sa|ag|inc|llc|ltd|gmbh|sarl|bv|nv|oy|ab|spa|plc|corp|co)\b",
        " ",
        query_clean,
        flags=re.IGNORECASE,
    )
    core_query = re.sub(r"\s+", " ", core_query).strip() or query_clean

    trusted_domains = [
        "startupticker.ch",
        "venturelab.swiss",
        "techcrunch.com",
        "crunchbase.com",
        "pitchbook.com",
        "sifted.eu",
        "eu-startups.com",
        "forbes.com",
        "reuters.com",
        "bloomberg.com",
    ]
    startup_tokens = []
    for t in re.split(r"[^a-z0-9]+", core_query.lower()):
        if len(t) >= 3 and t not in legal_suffixes:
            startup_tokens.append(t)
    if not startup_tokens:
        startup_tokens = [t for t in re.split(r"[^a-z0-9]+", query_clean.lower()) if len(t) >= 3]

    preferred_domain = ""
    if preferred_url:
        parsed_preferred = urlparse(preferred_url)
        preferred_domain = parsed_preferred.netloc.lower().replace("www.", "")

    blocked_nsfw_terms = [
        "porn", "porno", "xxx", "adult", "sex", "xvideos", "xnxx", "pornhub", "redtube",
        "youporn", "brazzers", "onlyfans", "escort", "cams", "camgirl",
    ]

    enriched_queries = [
        query_clean,
        f"\"{core_query}\" startup",
        f"\"{core_query}\" founders leadership team",
        f"\"{core_query}\" CEO CTO CFO COO CMO CPO management",
        f"\"{core_query}\" funding investors valuation",
        f"\"{core_query}\" deep tech startup",
        f"\"{core_query}\" headquarters US Europe footprint",
        f"\"{core_query}\" technology patents competitors alternatives",
        f"site:startupticker.ch \"{core_query}\"",
        f"site:venturelab.swiss \"{core_query}\"",
    ]
    if preferred_domain:
        enriched_queries.extend(
            [
                f"site:{preferred_domain} {core_query}",
                f"\"{preferred_domain}\" {core_query} startup",
            ]
        )

    cleaned_results: List[Dict[str, Any]] = []
    seen_urls = set()
    search_errors: List[str] = []

    def fetch_with_fallback(ddgs_client: DDGS, q: str, limit: int) -> List[Dict[str, Any]]:
        """
        Try multiple DDGS backends to avoid backend-specific outages.
        """
        backend_errors: List[str] = []
        for backend in ("lite", "html", "auto"):
            try:
                return list(
                    ddgs_client.text(
                        q,
                        max_results=limit,
                        backend=backend,
                        safesearch="strict",
                    )
                )
            except TypeError:
                # Older duckduckgo-search versions don't support safesearch keyword.
                try:
                    return list(ddgs_client.text(q, max_results=limit, backend=backend))
                except Exception:
                    backend_errors.append(f"{backend}: incompatible safesearch and fallback failed")
                    continue
            except Exception:
                backend_errors.append(f"{backend}: request failed")
                continue
        if backend_errors:
            search_errors.append(f"Query '{q}' failed across backends ({'; '.join(backend_errors)})")
        return []

    with DDGS() as ddgs:
        per_query = max(5, max_results // len(enriched_queries))
        for q in enriched_queries:
            try:
                results = fetch_with_fallback(ddgs, q, per_query)
                for r in results:
                    href = (r.get("href") or r.get("url") or "").strip()
                    if not href:
                        continue
                    lower_href = href.lower()
                    text_blob = (
                        f"{r.get('title', '')} {r.get('body') or r.get('snippet') or ''} {lower_href}"
                    ).lower()
                    name_match = any(tok in text_blob for tok in startup_tokens) if startup_tokens else True
                    if any(skip in lower_href for skip in ["login", "password"]):
                        continue
                    if any(term in text_blob for term in blocked_nsfw_terms):
                        continue
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    cleaned_results.append(
                        {
                            "title": r.get("title", "").strip(),
                            "body": (r.get("body") or r.get("snippet") or "").strip(),
                            "href": href,
                            "name_match": name_match,
                        }
                    )
            except Exception:
                search_errors.append(f"Query loop failed: '{q}'")
                continue

        # Fallback: if targeted queries are sparse/rate-limited, do a broad pass.
        if len(cleaned_results) < 6:
            fallback_queries = [query, f"{query} company", f"{query} startup"]
            for fq in fallback_queries:
                try:
                    results = fetch_with_fallback(ddgs, fq, 10)
                    for r in results:
                        href = (r.get("href") or r.get("url") or "").strip()
                        if not href or href in seen_urls:
                            continue
                        lower_href = href.lower()
                        text_blob = (
                            f"{r.get('title', '')} {r.get('body') or r.get('snippet') or ''} {lower_href}"
                        ).lower()
                        name_match = any(tok in text_blob for tok in startup_tokens) if startup_tokens else True
                        if any(skip in lower_href for skip in ["login", "password"]):
                            continue
                        if any(term in text_blob for term in blocked_nsfw_terms):
                            continue
                        seen_urls.add(href)
                        cleaned_results.append(
                            {
                                "title": r.get("title", "").strip(),
                                "body": (r.get("body") or r.get("snippet") or "").strip(),
                                "href": href,
                                "name_match": name_match,
                            }
                        )
                except Exception:
                    search_errors.append(f"Fallback query loop failed: '{fq}'")
                    continue

    keywords = [
        "founder", "ceo", "cto", "cfo", "coo", "cmo", "cpo", "leadership",
        "management", "co-founder", "raised", "series", "funding", "acquired",
        "acquisition", "review", "alternative", "competitor",
    ]

    def score_result(r: Dict[str, Any]) -> int:
        text = (r.get("title", "") + " " + r.get("body", "")).lower()
        score = sum(kw in text for kw in keywords)
        href = (r.get("href", "") or "").lower()
        domain = urlparse(href).netloc.lower()

        if any(td in domain for td in trusted_domains):
            score += 8
        if "startupticker.ch" in domain:
            score += 4
        if "venturelab.swiss" in domain:
            score += 4

        # Favor likely official or tightly relevant startup pages.
        if any(tok in domain for tok in startup_tokens):
            score += 5
        if any(tok in text for tok in startup_tokens):
            score += 3
        if r.get("name_match"):
            score += 12
        if preferred_domain and preferred_domain in domain:
            score += 20
        if preferred_url and href.rstrip("/") == preferred_url.rstrip("/").lower():
            score += 30

        # Penalize low-signal utility pages.
        if any(skip in href for skip in ["login", "signup", "privacy", "terms"]):
            score -= 3
        return score

    cleaned_results.sort(key=score_result, reverse=True)

    # Keep output anchored to the startup entity first.
    name_matched = [r for r in cleaned_results if r.get("name_match")]
    if len(name_matched) >= 3:
        cleaned_results = name_matched + [r for r in cleaned_results if not r.get("name_match")]

    # Ensure user-provided URL is represented in sources.
    if preferred_url:
        preferred_norm = preferred_url.rstrip("/").lower()
        has_preferred = any((r.get("href", "").rstrip("/").lower() == preferred_norm) for r in cleaned_results)
        if not has_preferred:
            cleaned_results.insert(
                0,
                {
                    "title": f"Official website ({preferred_domain or 'provided URL'})",
                    "body": "User-provided startup website.",
                    "href": preferred_url,
                    "name_match": True,
                },
            )

    # If everything failed, surface meaningful diagnostics instead of silent "no signal."
    if not cleaned_results and search_errors:
        brief_errors = " | ".join(search_errors[:3])
        raise RuntimeError(
            "Web search failed on this deployment environment. "
            "This is usually dependency/network/runtime related. "
            f"Details: {brief_errors}"
        )

    return cleaned_results


def build_llm_prompt(startup_name: str, search_results: List[Dict[str, Any]]) -> str:
    current_date = datetime.datetime.now().strftime("%B %Y")
    lines = [
        f"Startup: {startup_name.strip()}",
        f"Current Date: {current_date}",
        "Below are raw web search results about this startup. Use ONLY these results.",
        "Translate any French or German text to English.",
        "=== SEARCH RESULTS START ===",
    ]
    for idx, r in enumerate(search_results, start=1):
        lines.append(f"\n[Result {idx}]")
        if r.get("title"):
            lines.append(f"Title: {r['title'].strip()}")
        if r.get("href"):
            lines.append(f"URL: {r['href'].strip()}")
        if r.get("body"):
            lines.append(f"Snippet: {r['body'].strip()}")

    lines.append("\n=== SEARCH RESULTS END ===\n")
    lines.append(
        "TASK:\n"
        "You are a ruthless Swiss Deep Tech Venture Capitalist acting on behalf of Lucian at EuroUS Ventures. "
        "Use only the supplied results.\n\n"
        "Carefully scan for:\n"
        "- Academic pedigree and scientific moat.\n"
        "- Geo-arbitrage (EU R&D vs US commercial expansion).\n"
        "- Funding rounds, investors, valuation signals.\n"
        "- Leadership with C-level titles (CEO, CTO, CFO, COO, CMO, CPO and full-title variants).\n"
        "- Non-funding milestones, product launches, operational traction.\n"
        "- Competitors and alternative solutions explicitly mentioned.\n\n"
        "Icebreaker quality rules:\n"
        "- Exactly 3 icebreaker bullets.\n"
        "- Ready-to-say conversational openers for founder calls.\n"
        "- Each icebreaker MUST be a question ending with '?'.\n"
        "- Keep each short, slightly witty, and grounded in concrete facts.\n"
        "- If leadership exists, the first icebreaker must use that.\n\n"
        "Good examples:\n"
        "- \"You shipped Gen 1 quickly for deep tech - what unlocked that execution speed?\"\n"
        "- \"Your CEO came from [background] - what shaped your current thesis?\"\n"
        "- \"You hit [milestone] early - what risk did that de-risk first?\"\n\n"
        "Output structure (exact):\n"
        "# [Startup Name]\n"
        "**Deep Tech Value Prop**: [One-sentence description]\n\n"
        "## EuroUS Scorecard (1–5) – Summary\n"
        "- Scientific depth / IP defensibility — [1–5]/5 — [short tag]\n"
        "- EuroUS geo-arbitrage potential — [1–5]/5 — [short tag]\n"
        "- US go-to-market readiness — [1–5]/5 — [short tag]\n"
        "- Capital efficiency & funding fit — [1–5]/5 — [short tag]\n"
        "- Strategic differentiation vs incumbents — [1–5]/5 — [short tag]\n\n"
        "## Section 1 – The Hook & Origins\n"
        "- **Icebreakers (3 bullets):** [3 bullets]\n"
        "- **Founders & Leadership:** [bullets]\n"
        "- **Scientific Pedigree:** [bullets]\n"
        "- **Geo-Arbitrage & Expansion:** [bullets]\n"
        "- **Traction & Funding:** [bullets]\n\n"
        "## Section 2 – The EuroUS Lens\n"
        "- **Technical & Market Risks (The Bear Case):** [bullets]\n"
        "- **Interrogation Questions:** [3 questions]\n\n"
        "## Section 3 – Competitor Radar\n"
        "- [2-3 bullets]\n\n"
        "## EuroUS Scorecard – Details\n"
        "- [one rationale bullet per axis]\n\n"
        "Formatting rules:\n"
        "- No emojis.\n"
        "- Wrap VC-critical metrics in inline code: `CHF 1.8M`, `Series A`, `TRL 7`, `18.8%`.\n"
        "- Never hallucinate; if missing, say 'No public data found'.\n"
        "- Do not output sources section or external links.\n"
    )
    return "\n".join(lines)


def ensure_config_ok() -> None:
    api_key = get_config_value("OPENAI_API_KEY") or get_config_value("DEEPINFRA_API_KEY")
    if not api_key:
        st.error("Missing API key. Please set OPENAI_API_KEY or DEEPINFRA_API_KEY in your terminal.")
        st.stop()


def get_config_value(key: str, default: str | None = None) -> str | None:
    """
    Read config from environment first, then Streamlit secrets.
    """
    env_val = os.environ.get(key)
    if env_val:
        return env_val
    try:
        if key in st.secrets:
            val = st.secrets[key]
            return str(val) if val is not None else default
    except Exception:
        pass
    return default


def create_openai_client() -> OpenAI:
    api_key = get_config_value("OPENAI_API_KEY") or get_config_value("DEEPINFRA_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY/DEEPINFRA_API_KEY.")
    base_url = get_config_value("OPENAI_BASE_URL", "https://api.deepinfra.com/v1/openai")
    return OpenAI(api_key=api_key, base_url=base_url)


def call_llm(prompt: str) -> str:
    client = create_openai_client()
    model_name = get_config_value("LLM_MODEL_NAME", "meta-llama/Meta-Llama-3-70B-Instruct")
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a skeptical VC analyst. Use only provided evidence. No emojis. "
                    "No fluff. Capture C-level roles explicitly when present. "
                    "Icebreakers must be short, conversational call-openers phrased as questions."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=1600,
    )
    return (response.choices[0].message.content or "").strip()


# -----------------------------
# UI Helpers
# -----------------------------

def get_zurich_time_label() -> str:
    now_ch = datetime.datetime.now(ZoneInfo("Europe/Zurich"))
    return f"Time in Zürich: {now_ch.strftime('%H:%M')}"


def render_header() -> tuple[str, bool]:
    time_label = get_zurich_time_label()
    st.markdown(
        f"""
        <div class="shift-hero">
            <div class="shift-hero-left">
                <img src="{EUROUS_LOGO_URL}" class="shift-logo-mini" alt="EuroUS Ventures logo" />
                <h1 class="shift-hero-title">Smart Briefs</h1>
                <div class="shift-hero-subline typewriter-text">Hi Lucian · {time_label}</div>
            </div>
            <div class="shift-hero-right">
                <div class="shift-hero-right-copy">
                    High-conviction call prep for deep-tech founders, with evidence-first scoring.
                </div>
                <div class="shift-hero-right-status">
                    <div class="status-strip">
                        <span class="status-label">System status</span>
                        <span class="status-state">
                            <span class="status-online">ONLINE</span>
                            <span class="status-refresh">SUBMIT A NEW QUERY?</span>
                        </span>
                        <span class="status-dots">
                            <span class="status-dot"></span>
                            <span class="status-dot"></span>
                            <span class="status-dot"></span>
                            <span class="status-dot"></span>
                            <span class="status-dot"></span>
                        </span>
                    </div>
                    <div class="system-telemetry">
                        <div class="system-telemetry-title">Signal grid</div>
                        <div class="system-telemetry-row">
                            <span class="system-telemetry-name">01 Source intake</span>
                            <span class="system-telemetry-val">ACTIVE</span>
                        </div>
                        <div class="system-telemetry-row">
                            <span class="system-telemetry-name">02 Evidence quality</span>
                            <span class="system-telemetry-val">LOCKED</span>
                        </div>
                        <div class="system-telemetry-row">
                            <span class="system-telemetry-name">03 VC scoring model</span>
                            <span class="system-telemetry-val">READY</span>
                        </div>
                        <div class="system-telemetry-row">
                            <span class="system-telemetry-name">04 Reliability mode</span>
                            <span class="system-telemetry-val">{st.session_state.get("reliability_mode", "STRICT").upper()}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="controls-row"></div>', unsafe_allow_html=True)
    reliability_col, motion_col, toggle_col, print_col = st.columns([2.45, 1.85, 1.55, 1.65])
    with reliability_col:
        st.selectbox(
            "Reliability mode",
            options=["Strict", "Balanced"],
            key="reliability_mode",
            label_visibility="collapsed",
        )
        reliability_mode = st.session_state.get("reliability_mode", "Balanced")
        badge_class = "strict" if reliability_mode == "Strict" else "balanced"
        st.markdown(
            f"""
            <div class="reliability-badge-wrap">
                <span class="reliability-badge {badge_class}">{reliability_mode}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with motion_col:
        st.selectbox(
            "Motion",
            options=["Subtle", "Medium", "Off"],
            key="motion_mode",
            label_visibility="collapsed",
        )
    with toggle_col:
        st.toggle("Dark mode", key="dark_mode")
    with print_col:
        st.toggle("Print preview", key="print_preview_mode")

    st.markdown('<div class="control-divider"></div>', unsafe_allow_html=True)
    query = st.text_input(
        "Startup Search",
        placeholder="e.g. Enantios, Figma, 'Mistral AI - mistral.ai'",
        label_visibility="collapsed",
    )
    generate_clicked = st.button("Generate Brief", use_container_width=True)
    return query.strip(), generate_clicked


def parse_scorecard_summary(brief_markdown: str) -> List[Dict[str, str]]:
    cards: List[Dict[str, str]] = []
    pattern = r"-\s*(.*?)\s+—\s+([0-9]+(?:\.[0-9]+)?)/5\s+—\s+(.*)"
    for line in brief_markdown.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            axis, score, tag = match.groups()
            cards.append({"axis": axis.strip(), "score": score.strip(), "tag": tag.strip()})
    return cards


def strip_scorecard_summary_section(text: str) -> str:
    pattern = r"## EuroUS Scorecard \(1–5\) – Summary[\s\S]*?(?=\n## )"
    return re.sub(pattern, "", text, flags=re.MULTILINE).strip()


def strip_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "[\U0001F300-\U0001F9FF\U0001FA00-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)


def emphasize_vc_inline_code(text: str) -> str:
    patterns = [
        r"(?<!`)(?:CHF|USD|EUR|GBP)\s?\d[\d,\.]*(?:\s?(?:million|billion|m|bn|M|B))?(?!`)",
        r"(?<!`)(?:\$|€|£)\s?\d[\d,\.]*(?:\s?(?:million|billion|m|bn|M|B))?(?!`)",
        r"(?<!`)\b\d+(?:\.\d+)?%(?!`)",
        r"(?<!`)\b(?:Pre[-\s]?Seed|Seed|Series\s[A-E]|IPO|post-money|pre-money)(?!`)\b",
        r"(?<!`)\bTRL\s?\d+(?!`)\b",
    ]
    out = text
    for pattern in patterns:
        out = re.sub(pattern, lambda m: f"`{m.group(0)}`", out, flags=re.IGNORECASE)
    return out


def enforce_icebreaker_questions(text: str) -> str:
    """
    Ensure Icebreakers are opener-style questions even when model output drifts.
    """
    lines = text.splitlines()
    out: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)

        if "Icebreakers" not in line:
            i += 1
            continue

        # Capture immediate bullet lines under Icebreakers block.
        j = i + 1
        captured: List[str] = []
        while j < len(lines):
            nxt = lines[j]
            stripped = nxt.strip()
            if stripped.startswith("- **") or stripped.startswith("## "):
                break
            if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("o ") or stripped.startswith("• "):
                captured.append(nxt)
            j += 1

        if captured:
            # Remove already appended captured originals from output by not copying them;
            # replace with normalized question bullets.
            normalized: List[str] = []
            for idx, raw in enumerate(captured[:3], start=1):
                content = raw.strip()
                content = re.sub(r"^[-*o•]\s+", "", content)
                content = re.sub(r"^Bullet\s*\d+\s*:\s*", "", content, flags=re.IGNORECASE)
                content = content.strip()
                if not content:
                    continue
                if not content.endswith("?"):
                    content = content.rstrip(".")
                    if idx == 1:
                        content = f"{content} - what shaped that path?"
                    elif idx == 2:
                        content = f"{content} - what surprised you most there?"
                    else:
                        content = f"{content} - what did that de-risk first?"
                normalized.append(f"  - {content}")

            # Remove originals that may have been appended later by skipping them.
            out.extend(normalized)
            i = j
            continue

        i += 1

    return "\n".join(out)


def enhance_icebreakers(text: str, startup_name: str) -> str:
    """
    Upgrade icebreakers to be specific, conversational, and call-ready.
    """
    lines = text.splitlines()
    startup = startup_name.strip() or "the company"

    def rewrite_line(raw_line: str, idx: int, context: str) -> str:
        content = raw_line.strip()
        content = re.sub(r"^[-*o•]\s+", "", content)
        content = re.sub(r"^Bullet\s*\d+\s*:\s*", "", content, flags=re.IGNORECASE)
        content = content.strip()
        if not content:
            return ""

        lower = content.lower()
        generic = (
            "no public data found" in lower
            or lower.startswith("how does")
            or lower.startswith("what is")
            or len(content) < 38
        )
        if generic:
            if idx == 1:
                return f"  - You move fast in a hard category - what non-obvious founder decision gave {startup} its current edge?"
            if idx == 2:
                return f"  - Which recent signal (customer, product, or team) changed your conviction most in the last 6 months?"
            return f"  - If your current plan fails, what is the first pivot you would run and why?"

        if not content.endswith("?"):
            content = content.rstrip(".")
            if idx == 1:
                content = f"{content} - what shaped that decision?"
            elif idx == 2:
                content = f"{content} - what surprised you most there?"
            else:
                content = f"{content} - what risk did that de-risk first?"
        return f"  - {content}"

    out: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if "Icebreakers" not in line:
            i += 1
            continue

        j = i + 1
        captured: List[str] = []
        while j < len(lines):
            nxt = lines[j]
            stripped = nxt.strip()
            if stripped.startswith("- **") or stripped.startswith("## "):
                break
            if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("o ") or stripped.startswith("• "):
                captured.append(nxt)
            j += 1

        rebuilt: List[str] = []
        for idx in range(3):
            source = captured[idx] if idx < len(captured) else ""
            rewritten = rewrite_line(source, idx + 1, text)
            if rewritten:
                rebuilt.append(rewritten)

        while len(rebuilt) < 3:
            fallback_idx = len(rebuilt) + 1
            rebuilt.append(
                rewrite_line("", fallback_idx, text)
                or f"  - What is the single most counterintuitive thing investors miss about {startup}?"
            )

        out.extend(rebuilt[:3])
        i = j

    return "\n".join(out)


def upgrade_competitor_radar(text: str) -> str:
    """
    Add strategic tags to competitor bullets: [Direct], [Indirect], [Incumbent].
    """
    pattern = r"(## Section 3 – Competitor Radar\n)([\s\S]*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return text

    header, body = match.groups()
    lines = body.splitlines()
    tagged: List[str] = []
    for line in lines:
        s = line.strip()
        if not s.startswith("- "):
            if s:
                tagged.append(line)
            continue
        core = s[2:].strip()
        if core.lower() == "no public data found":
            tagged.append("- No public data found")
            continue
        if core.startswith("`[") or core.startswith("["):
            tagged.append(f"- {core}")
            continue

        low = core.lower()
        if any(k in low for k in ["incumbent", "legacy", "oracle", "sap", "microsoft", "google", "aws", "siemens"]):
            tag = "Incumbent"
        elif any(k in low for k in ["adjacent", "alternative", "indirect", "workflow", "platform"]):
            tag = "Indirect"
        else:
            tag = "Direct"
        tagged.append(f"- `[{tag}]` {core}")

    if not tagged:
        tagged = ["- No public data found"]
    if len(tagged) == 1 and "No public data found" not in tagged[0]:
        tagged.append("- `[Indirect]` Adjacent workflow or incumbent alternatives not clearly surfaced in public data.")

    rebuilt = header + "\n".join(tagged).rstrip() + "\n"
    return text[:match.start()] + rebuilt + text[match.end():]


def lock_low_confidence_sections(text: str, evidence: Dict[str, Any]) -> str:
    """
    Lock weak sections instead of returning low-quality speculative content.
    """
    if not evidence:
        return text
    signals = evidence.get("signals", {}) or {}
    out = text

    def lock_block(src: str, anchor: str, message: str) -> str:
        patt = rf"({re.escape(anchor)})(.*?)(?=\n- \*\*|\n## |\Z)"
        return re.sub(patt, rf"\1 {message}", src, flags=re.MULTILINE | re.DOTALL)

    if not signals.get("leadership", False):
        out = lock_block(out, "- **Founders & Leadership:**", "`[LOCKED: weak public leadership signal]` Add official about/team page or founder profile URL.")
    if not signals.get("funding", False):
        out = lock_block(out, "- **Traction & Funding:**", "`[LOCKED: weak funding signal]` Add Crunchbase/PitchBook/company press release URL.")

    if not signals.get("competitors", False):
        out = re.sub(
            r"(## Section 3 – Competitor Radar\n)([\s\S]*?)(?=\n## |\Z)",
            r"\1- `[LOCKED: weak competitor signal]` Provide category keyword or top 2 known rivals for stronger radar.\n",
            out,
            flags=re.MULTILINE,
        )
    return out


def render_source_quality_panel() -> None:
    ev = st.session_state.get("evidence_quality") or {}
    if not ev:
        return
    with st.expander("Source Quality Panel", expanded=False):
        thresholds = ev.get("thresholds", {}) or {}
        st.markdown(
            f"- Score: `{ev.get('score', 'n/a')}`\n"
            f"- Trusted sources hit: `{ev.get('trusted_hits', 'n/a')}`\n"
            f"- Unique domains: `{ev.get('unique_domains', 'n/a')}`\n"
            f"- Startup relevance hits: `{ev.get('startup_relevance_hits', 'n/a')}`\n"
            f"- Enough for reliable brief: `{ev.get('enough', False)}`"
        )
        if thresholds:
            st.caption(
                f"Thresholds ({thresholds.get('mode', 'n/a')}): "
                f"trusted>={thresholds.get('min_trusted_hits', 'n/a')}, "
                f"relevance>={thresholds.get('min_startup_relevance_hits', 'n/a')}, "
                f"results>={thresholds.get('min_results', 'n/a')}"
            )
        signals = ev.get("signals", {}) or {}
        st.markdown(
            f"Signals - leadership: `{signals.get('leadership', False)}`, funding: `{signals.get('funding', False)}`, "
            f"competitors: `{signals.get('competitors', False)}`, traction: `{signals.get('traction', False)}`"
        )
        reasons = ev.get("reasons") or []
        if reasons:
            st.caption("Weak areas: " + "; ".join(reasons))
        top_domains = ev.get("top_domains") or []
        if top_domains:
            st.markdown("Top domains in this brief:")
            for dom, count in top_domains:
                st.markdown(f"- `{dom}` ({count})")


def render_brief_history_panel() -> None:
    history = st.session_state.get("brief_history", [])
    if not history:
        return
    with st.expander("Brief History (last 5)", expanded=False):
        labels = [
            f"{idx + 1}. {item.get('query', 'Unknown')} · {item.get('timestamp', '')} · "
            f"{'Low-confidence' if item.get('low_confidence') else 'Normal'}"
            for idx, item in enumerate(history)
        ]
        selected = st.selectbox("Recent briefs", options=list(range(len(labels))), format_func=lambda i: labels[i], key="history_select_idx")
        load_col, clear_col = st.columns(2)
        if load_col.button("Load selected brief", use_container_width=True, key="load_history_brief"):
            chosen = history[selected]
            st.session_state["brief_markdown"] = chosen.get("brief_markdown")
            st.session_state["search_results"] = chosen.get("search_results", [])
            st.session_state["last_query"] = chosen.get("query", "")
            st.session_state["low_confidence"] = chosen.get("low_confidence", False)
            st.session_state["evidence_quality"] = chosen.get("evidence_quality")
            st.rerun()
        if clear_col.button("Clear history", use_container_width=True, key="clear_history_briefs"):
            st.session_state["brief_history"] = []
            st.rerun()


def split_intro_and_section_one(content: str) -> tuple[str, str]:
    match = re.search(r"\n##\s*Section 1\b", content)
    if not match:
        return content.strip(), ""
    return content[:match.start()].strip(), content[match.start():].strip()


def _evidence_signals(search_results: List[Dict[str, Any]]) -> Dict[str, bool]:
    blob = " ".join(
        f"{r.get('title', '')} {r.get('body', '')} {r.get('href', '')}" for r in search_results
    ).lower()
    leadership_terms = ["founder", "co-founder", "ceo", "cto", "cfo", "coo", "cmo", "cpo", "leadership"]
    funding_terms = ["seed", "series", "raised", "funding", "investor", "valuation", "round"]
    competitor_terms = ["competitor", "alternative", "vs", "rival", "incumbent", "market leader"]
    traction_terms = ["launch", "pilot", "customer", "revenue", "deployment", "installed", "partnership"]
    return {
        "leadership": any(t in blob for t in leadership_terms),
        "funding": any(t in blob for t in funding_terms),
        "competitors": any(t in blob for t in competitor_terms),
        "traction": any(t in blob for t in traction_terms),
    }


def evaluate_evidence_quality(
    startup_name: str,
    search_results: List[Dict[str, Any]],
    reliability_mode: str = "Balanced",
) -> Dict[str, Any]:
    """
    Strict pre-LLM quality gate: block generation when public signal is too weak.
    """
    trusted_domains = [
        "startupticker.ch",
        "venturelab.swiss",
        "techcrunch.com",
        "crunchbase.com",
        "pitchbook.com",
        "sifted.eu",
        "eu-startups.com",
        "reuters.com",
        "bloomberg.com",
    ]
    startup_tokens = [t for t in re.split(r"[^a-z0-9]+", startup_name.lower()) if len(t) >= 3]

    # Adaptive thresholds: strict enough for quality, but not so strict that most queries fail.
    is_balanced = reliability_mode.lower() == "balanced"
    min_trusted_hits = 1 if is_balanced else 2
    min_startup_relevance_hits = 3 if is_balanced else 6
    min_results = 6 if is_balanced else 10
    sample_limit = min(len(search_results), 50)

    unique_domains = set()
    domain_counts: Dict[str, int] = {}
    trusted_hits = 0
    startup_relevance_hits = 0
    for r in search_results[:sample_limit]:
        href = (r.get("href") or "").strip().lower()
        title = (r.get("title") or "").strip().lower()
        body = (r.get("body") or "").strip().lower()
        dom = urlparse(href).netloc
        if dom:
            unique_domains.add(dom)
            domain_counts[dom] = domain_counts.get(dom, 0) + 1
        if any(td in dom for td in trusted_domains):
            trusted_hits += 1
        if any(tok in dom or tok in title or tok in body for tok in startup_tokens):
            startup_relevance_hits += 1

    signals = _evidence_signals(search_results)
    score = 0
    reasons: List[str] = []

    if len(search_results) >= min_results:
        score += 2
    else:
        reasons.append(f"fewer than {min_results} search results")

    if len(unique_domains) >= 4:
        score += 2
    else:
        reasons.append("low domain diversity")

    if trusted_hits >= min_trusted_hits:
        score += 3
    elif trusted_hits >= 2:
        score += 1
    else:
        reasons.append(f"trusted-source hits below threshold ({trusted_hits}/{min_trusted_hits})")

    if startup_relevance_hits >= min_startup_relevance_hits:
        score += 2
    else:
        reasons.append(
            f"startup relevance hits below threshold ({startup_relevance_hits}/{min_startup_relevance_hits})"
        )

    if signals.get("leadership"):
        score += 1
    else:
        reasons.append("missing leadership signal")
    if signals.get("funding"):
        score += 1
    else:
        reasons.append("missing funding signal")
    if signals.get("competitors"):
        score += 1
    else:
        reasons.append("missing competitor signal")

    enough = (
        score >= 8
        and len(unique_domains) >= 3
        and trusted_hits >= min_trusted_hits
        and startup_relevance_hits >= min_startup_relevance_hits
        and (signals.get("leadership") or signals.get("funding"))
    )
    return {
        "enough": enough,
        "score": score,
        "trusted_hits": trusted_hits,
        "unique_domains": len(unique_domains),
        "startup_relevance_hits": startup_relevance_hits,
        "signals": signals,
        "reasons": reasons[:4],
        "top_domains": sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:6],
        "thresholds": {
            "min_trusted_hits": min_trusted_hits,
            "min_startup_relevance_hits": min_startup_relevance_hits,
            "min_results": min_results,
            "mode": reliability_mode,
        },
    }


def _brief_quality_score(brief: str, signals: Dict[str, bool]) -> tuple[int, List[str]]:
    text = (brief or "").lower()
    score = 0
    missing: List[str] = []

    must_sections = [
        "## section 1",
        "## section 2",
        "## section 3",
        "## eurous scorecard",
        "interrogation questions",
        "icebreakers",
    ]
    for sec in must_sections:
        if sec in text:
            score += 2
        else:
            missing.append(sec)

    # Strongly reward inclusion of named C-level roles.
    c_level_hits = sum(role in text for role in ["ceo", "cto", "cfo", "coo", "cmo", "cpo"])
    score += min(6, c_level_hits)

    no_data_hits = text.count("no public data found")
    if no_data_hits <= 2:
        score += 4
    elif no_data_hits <= 5:
        score += 1
    else:
        score -= 4

    if signals.get("leadership") and c_level_hits == 0:
        score -= 3
        missing.append("leadership evidence used")
    if signals.get("funding") and "funding" not in text and "series" not in text:
        score -= 3
        missing.append("funding evidence used")
    if signals.get("competitors") and "competitor" not in text and "alternative" not in text:
        score -= 2
        missing.append("competitor evidence used")
    if signals.get("traction") and "traction" not in text and "milestone" not in text:
        score -= 1
        missing.append("traction evidence used")

    return score, missing


def _build_repair_prompt(
    startup_name: str,
    base_prompt: str,
    draft: str,
    missing_items: List[str],
    search_results: List[Dict[str, Any]],
) -> str:
    evidence_lines: List[str] = []
    for i, r in enumerate(search_results[:10], start=1):
        title = r.get("title", "").strip()
        body = r.get("body", "").strip()
        href = r.get("href", "").strip()
        evidence_lines.append(f"{i}. {title} | {body} | {href}")

    repair_instructions = (
        f"You produced a weak draft for {startup_name}. Rewrite it fully.\n"
        "Do not drop any required section. Keep concise but specific.\n"
        "Missing/weak areas detected:\n"
        + "\n".join(f"- {m}" for m in missing_items[:10])
        + "\n\nUse this high-signal evidence first:\n"
        + "\n".join(evidence_lines)
        + "\n\nPrevious weak draft (for reference only, do not copy errors):\n"
        + draft
    )
    return f"{base_prompt}\n\n--- REPAIR PASS ---\n{repair_instructions}"


def generate_consistent_brief(startup_name: str, search_results: List[Dict[str, Any]]) -> str:
    """
    Two-pass generation:
    1) Normal deterministic draft.
    2) Automatic repair draft only if quality gate is weak.
    Returns the best-scoring draft.
    """
    base_prompt = build_llm_prompt(startup_name, search_results)
    first = call_llm(base_prompt)
    signals = _evidence_signals(search_results)
    score_first, missing_first = _brief_quality_score(first, signals)
    if score_first >= 14:
        return first

    repair_prompt = _build_repair_prompt(
        startup_name=startup_name,
        base_prompt=base_prompt,
        draft=first,
        missing_items=missing_first,
        search_results=search_results,
    )
    second = call_llm(repair_prompt)
    score_second, _ = _brief_quality_score(second, signals)
    return second if score_second >= score_first else first


def generate_best_of_multiple_attempts(
    startup_name: str,
    reliability_mode: str,
    attempts: int = 3,
    preferred_url: str | None = None,
) -> Dict[str, Any]:
    """
    Run multiple search + generation attempts and return the best candidate.
    This reduces one-click variance when public search results fluctuate.
    """
    best_candidate: Dict[str, Any] | None = None
    best_rank = -10_000
    no_signal_attempts = 0
    attempt_errors: List[str] = []
    best_evidence_seen: Dict[str, Any] | None = None

    for _ in range(max(1, attempts)):
        try:
            results = search_duckduckgo(startup_name, max_results=30, preferred_url=preferred_url)
        except Exception as e:
            attempt_errors.append(str(e))
            continue

        if not results:
            no_signal_attempts += 1
            continue

        evidence = evaluate_evidence_quality(
            startup_name,
            results,
            reliability_mode=reliability_mode,
        )

        if (
            best_evidence_seen is None
            or evidence.get("score", 0) > best_evidence_seen.get("score", 0)
        ):
            best_evidence_seen = evidence

        # Hard floor: do not draft briefs when zero startup-name relevance is detected.
        if evidence.get("startup_relevance_hits", 0) == 0:
            continue

        # In strict mode, skip weak evidence attempts and keep trying.
        if reliability_mode == "Strict" and not evidence.get("enough", False):
            continue

        try:
            brief = generate_consistent_brief(startup_name, results)
        except Exception as e:
            attempt_errors.append(str(e))
            continue

        brief_score, _ = _brief_quality_score(brief, evidence.get("signals", {}) or {})
        evidence_score = int(evidence.get("score", 0))
        rank = (evidence_score * 3) + (brief_score * 2)

        candidate = {
            "brief_markdown": brief,
            "search_results": results,
            "evidence_quality": evidence,
            "low_confidence": not evidence.get("enough", False),
            "rank": rank,
            "brief_score": brief_score,
        }

        if rank > best_rank:
            best_rank = rank
            best_candidate = candidate

        # Early stop if this run is already very strong.
        if evidence.get("enough", False) and brief_score >= 16:
            break

    return {
        "best_candidate": best_candidate,
        "no_signal_attempts": no_signal_attempts,
        "attempt_errors": attempt_errors,
        "best_evidence_seen": best_evidence_seen,
    }


def estimate_generation_window_seconds() -> tuple[int, int]:
    """
    Estimate generation time using recent successful runs.
    Falls back to a conservative default window.
    """
    durations = st.session_state.get("generation_durations", []) or []
    valid = [int(d) for d in durations if isinstance(d, (int, float)) and d > 0]
    if not valid:
        return 35, 75
    avg = sum(valid) / max(1, len(valid))
    low = max(15, int(avg * 0.75))
    high = max(low + 12, int(avg * 1.35))
    return low, high


def render_scorecard_cards(cards: List[Dict[str, str]]) -> None:
    if not cards:
        return
    st.markdown('<div class="scorecard-heading">EuroUS Scorecard (1-5)</div>', unsafe_allow_html=True)
    st.markdown('<div class="scorecard-grid">', unsafe_allow_html=True)
    for card in cards[:6]:
        score_val = float(card["score"]) if card["score"] else 0.0
        filled = max(1, min(5, int(round(score_val))))
        dots = "●" * filled + "○" * (5 - filled)
        st.markdown(
            f"""
            <div class="scorecard-card">
                <div class="scorecard-axis">{escape(card["axis"])}</div>
                <div class="scorecard-line">{escape(card["score"])}/5 <span class="scorecard-dots">{dots}</span></div>
                <div class="scorecard-tag">{escape(card["tag"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_feedback() -> None:
    st.markdown("---")
    st.caption("Rate this brief to fine-tune the EuroUS extraction model.")
    slug = st.session_state.get("last_query", "default").replace(" ", "_")
    up_col, down_col = st.columns(2)
    thumbs_up = up_col.button("Helpful", use_container_width=True, key=f"thumbs_up_{slug}")
    thumbs_down = down_col.button("Needs Work", use_container_width=True, key=f"thumbs_down_{slug}")
    rating = "up" if thumbs_up else ("down" if thumbs_down else None)

    if rating and not st.session_state.get("feedback_submitted", False):
        st.session_state["feedback_submitted"] = True
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "query": st.session_state.get("last_query", ""),
            "rating": rating,
        }
        try:
            with Path("feedback_log.jsonl").open("a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
        st.toast("Thanks — feedback saved.")


def render_generation_loader(target) -> None:
    target.markdown(
        """
        <div class="brief-loader-wrap" aria-label="Generating brief">
            <div class="square sq1"></div>
            <div class="square sq2"></div>
            <div class="square sq3"></div>
            <div class="square sq4"></div>
            <div class="square sq5"></div>
            <div class="square sq6"></div>
            <div class="square sq7"></div>
            <div class="square sq8"></div>
            <div class="square sq9"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brief(brief_markdown: str, sources: List[Dict[str, Any]]) -> None:
    if not brief_markdown:
        return

    if st.session_state.get("low_confidence", False):
        ev = st.session_state.get("evidence_quality", {}) or {}
        st.warning(
            "Low-confidence brief: source signal was weak, but generation continued because Reliability mode is Balanced."
        )
        if ev:
            st.caption(
                f"Signal diagnostics - score: {ev.get('score', 'n/a')}, trusted sources: {ev.get('trusted_hits', 'n/a')}, "
                f"unique domains: {ev.get('unique_domains', 'n/a')}, startup relevance hits: {ev.get('startup_relevance_hits', 'n/a')}"
            )

    clean = strip_emojis(brief_markdown)
    tuned_icebreakers = enforce_icebreaker_questions(clean)
    upgraded_icebreakers = enhance_icebreakers(tuned_icebreakers, st.session_state.get("last_query", ""))
    upgraded_competitors = upgrade_competitor_radar(upgraded_icebreakers)
    maybe_locked = upgraded_competitors
    if st.session_state.get("low_confidence", False):
        maybe_locked = lock_low_confidence_sections(
            upgraded_competitors,
            st.session_state.get("evidence_quality", {}) or {},
        )
    emphasized = emphasize_vc_inline_code(maybe_locked)
    score_cards = parse_scorecard_summary(emphasized)
    without_summary = strip_scorecard_summary_section(emphasized)
    intro, section_body = split_intro_and_section_one(without_summary)

    if intro:
        st.markdown(intro, unsafe_allow_html=False)
    render_scorecard_cards(score_cards)
    if section_body:
        st.markdown(section_body, unsafe_allow_html=False)

    st.markdown("## Section 4 – Live Sources")
    if sources:
        for r in sources[:7]:
            title = r.get("title") or r.get("href") or "Source"
            href = r.get("href", "")
            if href:
                st.markdown(f"- [{title}]({href})")
    else:
        st.markdown("- No public data found")

    dossier_text = emphasized
    st.download_button(
        "Download Brief (.txt)",
        data=dossier_text,
        file_name="brief.txt",
        use_container_width=True,
    )

    render_source_quality_panel()
    if st.session_state.get("print_preview_mode", False):
        st.caption("Print preview is ON. Use browser print and Save as PDF for a cleaner one-page export.")
    render_feedback()


# -----------------------------
# Main App Logic
# -----------------------------

def init_session_state() -> None:
    defaults = {
        "brief_markdown": None,
        "last_query": "",
        "search_results": [],
        "error": None,
        "feedback_submitted": False,
        "motion_mode": "Subtle",
        "reliability_mode": "Balanced",
        "low_confidence": False,
        "evidence_quality": None,
        "brief_history": [],
        "history_select_idx": 0,
        "print_preview_mode": False,
        "generation_durations": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main() -> None:
    ensure_config_ok()
    inject_meta_tags()
    inject_mobile_and_print_css()
    inject_motion_mode_css()
    inject_print_preview_css()
    inject_dark_mode_css()
    init_session_state()

    query, generate_clicked = render_header()
    render_brief_history_panel()

    if generate_clicked:
        if not query:
            st.warning("Please enter a startup name (and optional URL) first.")
        else:
            startup_name, preferred_url = parse_startup_input(query)
            if not startup_name:
                st.warning("Please enter a startup name (and optional URL) first.")
                return

            st.session_state["brief_markdown"] = None
            st.session_state["search_results"] = []
            st.session_state["error"] = None
            st.session_state["last_query"] = startup_name
            st.session_state["feedback_submitted"] = False
            st.session_state["low_confidence"] = False
            st.session_state["evidence_quality"] = None

            loader_placeholder = st.empty()
            eta_placeholder = st.empty()
            render_generation_loader(loader_placeholder)
            with st.status("Initializing scan...", expanded=True) as status:
                try:
                    run_started = time.time()
                    eta_low, eta_high = estimate_generation_window_seconds()
                    eta_placeholder.caption(f"Estimated time: ~{eta_low}-{eta_high} seconds")
                    reliability_mode = st.session_state.get("reliability_mode", "Balanced")
                    status.update(label="Searching public signals and drafting brief...", state="running")
                    run = generate_best_of_multiple_attempts(
                        startup_name=startup_name,
                        reliability_mode=reliability_mode,
                        attempts=3,
                        preferred_url=preferred_url,
                    )
                    best_candidate = run.get("best_candidate")
                    best_evidence_seen = run.get("best_evidence_seen")

                    if not best_candidate:
                        if run.get("no_signal_attempts", 0) >= 3:
                            status.update(label="No public signal found.", state="error")
                            st.warning("No public signal found. The company might be in stealth. Try adding an exact URL.")
                            return

                        if best_evidence_seen and best_evidence_seen.get("startup_relevance_hits", 0) == 0:
                            st.session_state["evidence_quality"] = best_evidence_seen
                            status.update(label="No startup-matching signal found.", state="error")
                            st.warning(
                                "Search results did not reliably match this startup name. "
                                "Try adding the exact website URL or a more specific legal/company name."
                            )
                            return

                        if reliability_mode == "Strict" and best_evidence_seen and not best_evidence_seen.get("enough", False):
                            st.session_state["evidence_quality"] = best_evidence_seen
                            status.update(label="Insufficient high-quality public signal.", state="error")
                            st.warning(
                                "Signal quality is too weak for a reliable brief. "
                                "Add the exact company URL, country, or legal entity name and retry."
                            )
                            st.info(
                                f"Quality score: {best_evidence_seen['score']} | Trusted sources: {best_evidence_seen['trusted_hits']} | "
                                f"Unique domains: {best_evidence_seen['unique_domains']} | "
                                f"Startup relevance hits: {best_evidence_seen['startup_relevance_hits']}"
                            )
                            if best_evidence_seen.get("reasons"):
                                st.caption("Weak areas: " + "; ".join(best_evidence_seen["reasons"]))
                            return

                        status.update(label="Unable to generate a stable brief.", state="error")
                        details = run.get("attempt_errors", [])
                        if details:
                            st.caption("Attempt diagnostics: " + " | ".join(details[:2]))
                        st.warning("Could not generate a reliable brief this run. Please retry with an exact company URL.")
                        return

                    st.session_state["brief_markdown"] = best_candidate["brief_markdown"]
                    st.session_state["search_results"] = best_candidate["search_results"]
                    st.session_state["evidence_quality"] = best_candidate["evidence_quality"]
                    st.session_state["low_confidence"] = bool(best_candidate["low_confidence"])

                    if len(best_candidate["search_results"]) < 4:
                        st.info("Limited public signal found; brief quality may be lower. Try adding exact website URL.")

                    history = st.session_state.get("brief_history", [])
                    history.insert(
                        0,
                        {
                            "query": startup_name,
                            "timestamp": datetime.datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M"),
                            "brief_markdown": st.session_state["brief_markdown"],
                            "search_results": st.session_state["search_results"],
                            "low_confidence": st.session_state.get("low_confidence", False),
                            "evidence_quality": st.session_state.get("evidence_quality"),
                        },
                    )
                    st.session_state["brief_history"] = history[:5]
                    elapsed = int(time.time() - run_started)
                    durations = st.session_state.get("generation_durations", [])
                    durations.append(elapsed)
                    st.session_state["generation_durations"] = durations[-20:]
                    status.update(label=f"Dossier ready in {elapsed}s.", state="complete")
                except Exception as e:
                    st.session_state["error"] = str(e)
                    status.update(label="Error while generating dossier.", state="error")
                finally:
                    loader_placeholder.empty()
                    eta_placeholder.empty()

    if st.session_state.get("error"):
        st.error(
            "There was an issue generating this brief. This may be due to an API timeout or configuration problem.\n\n"
            f"Details: {st.session_state['error']}"
        )

    if st.session_state.get("brief_markdown"):
        render_brief(st.session_state["brief_markdown"], st.session_state.get("search_results", []))


if __name__ == "__main__":
    main()
