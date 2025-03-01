import React, { useState } from "react";
import { Chart, ArcElement, Tooltip } from "chart.js";
import { Pie } from "react-chartjs-2";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import "react-multi-carousel/lib/styles.css";

// Register Chart.js elements
Chart.register(ArcElement, Tooltip);

const Results = ({ results }) => {
  const [expanded, setExpanded] = useState(null);

  if (
    !results ||
    !results.smell_breakdown ||
    typeof results.total_smells !== "number"
  ) {
    return (
      <div style={{ marginTop: "40px", marginRight: "18px", fontSize: "18px" }}>
        No Results Yet
      </div>
    );
  }

  const smellTypes = [
    { name: "Large Class", color: "#ff6384" },
    { name: "Long Parameter List", color: "#00b4d8" },
    { name: "Long Method", color: "#cc65fe" },
    { name: "Long Message Chain", color: "#ffce56" },
    { name: "Long Base Class List", color: "#660f56" },
    { name: "Long Lambda Function", color: "#35cbac" },
    { name: "Long Element Chain", color: "#34495e" },
    { name: "Long Ternary Conditional Expression", color: "#ab4646" },
  ];

  const breakdown = results.smell_breakdown || {};

  const counts = smellTypes.map((type) => {
    return (
      breakdown[type.name]?.reduce(
        (acc, item) => acc + (item.lines ? item.lines.length : 0),
        0
      ) || 0
    );
  });

  const totalSmells = results.total_smells;
  const percentages = counts.map((count) =>
    totalSmells > 0 ? ((count / totalSmells) * 100).toFixed(1) : 0
  );

  const data = {
    labels: smellTypes.map((type) => type.name),
    datasets: [
      {
        data: percentages.map((p) => parseFloat(p)),
        backgroundColor: smellTypes.map((type) => type.color),
      },
    ],
  };

  const handleExpand = (panel) => () => {
    setExpanded(expanded === panel ? null : panel);
  };

  return (
    <div>
      <h3>Total Smells Detected: {results.total_smells}</h3>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          marginBottom: "20px",
        }}
      >
        {smellTypes.map((type) => (
          <div
            key={type.name}
            style={{
              display: "flex",
              alignItems: "center",
              marginRight: "15px",
              marginBottom: "10px",
            }}
          >
            <div
              style={{
                width: "15px",
                height: "15px",
                backgroundColor: type.color,
                marginRight: "5px",
              }}
            ></div>
            <span>
              {type.name}: {counts[smellTypes.indexOf(type)]}
            </span>
          </div>
        ))}
      </div>

      <div style={{ maxWidth: "280px", margin: "0 auto" }}>
        <Pie
          data={data}
          options={{
            plugins: {
              legend: {
                display: false,
              },
              tooltip: {
                callbacks: {
                  label: (tooltipItem) => {
                    const label = tooltipItem.label || "";
                    const value = tooltipItem.raw || 0;
                    return `${label}: ${value}%`;
                  },
                },
              },
            },
          }}
        />
      </div>

      {Object.entries(breakdown).map(([smellType, items]) => (
        <Accordion
          key={smellType}
          expanded={expanded === smellType}
          onChange={handleExpand(smellType)}
          style={{ marginBottom: "20px" }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">{smellType}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {items.map(({ file, lines, file_content }) => (
              <div key={file} style={{ fontFamily: "monospace" }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  File Path: {file} <br/> Line Number(s): {lines.join(", ")}
                </Typography>

                <pre
                  style={{
                    backgroundColor: "#f5f5f5",
                    padding: "10px",
                    borderRadius: "5px",
                    overflowX: "auto",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {file_content &&
                    file_content.map((lineText, index) => (
                      <div
                        key={index}
                        style={{
                          color: lines.includes(index + 1) ? "red" : "black",
                          textAlign: "start",
                        }}
                      >
                        {index + 1}: {lineText}
                      </div>
                    ))}
                </pre>
              </div>
            ))}
          </AccordionDetails>
        </Accordion>
      ))}
    </div>
  );
};

export default Results;
