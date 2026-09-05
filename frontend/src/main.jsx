import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { initEmbedHeight } from "./lib/embed.js";
import { WPR_MARK } from "./lib/wpr-logo.js";
import "./styles/tokens.css";
import "./styles/app.css";

// Tab icon: the typewriter roundel, from the same embedded asset the masthead
// uses — no extra file to host.
const icon = document.createElement("link");
icon.rel = "icon";
icon.href = WPR_MARK;
document.head.appendChild(icon);

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Report height to the host page when embedded in an iframe (seamless auto-resize).
initEmbedHeight("wpr-assessment-equity");
