import React from "react";
import { Chart, ArcElement, Tooltip } from "chart.js";
import { Pie } from "react-chartjs-2";

// Register Chart.js elements
Chart.register(ArcElement, Tooltip);

const Results = ({ results }) => {
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

  // Smell types and colors
  const smellTypes = [
    { name: "Large Class", color: "#ff6384" },
    { name: "Long Parameter List", color: "#36a2eb" },
    { name: "Long Method", color: "#cc65fe" },
    { name: "Long Message Chain", color: "#ffce56" },
    { name: "Long Base Class List", color: "#660f56 " },
    { name: "Long Lambda Function", color: "#35cbac" },
    { name: "Long Element Chain", color: "#34495e " },
    { name: "Long Ternary Conditional Expression", color: "#ab4646" },
  ];

  const breakdown = results.smell_breakdown;

  // Get counts for each smell type
  const counts = smellTypes.map((type) => breakdown[type.name]?.length || 0);

  // Calculate percentages proportional to counts
  const totalSmells = counts.reduce((sum, count) => sum + count, 0);
  const percentages = counts.map((count) =>
    totalSmells > 0 ? ((count / totalSmells) * 100).toFixed(1) : 0
  );

  // Prepare data for Pie chart
  const data = {
    labels: smellTypes.map((type) => type.name),
    datasets: [
      {
        data: percentages.map((p) => parseFloat(p)),
        backgroundColor: smellTypes.map((type) => type.color),
      },
    ],
  };

  return (
    <div>
      <h3>Total Smells Detected: {results.total_smells}</h3>

      {/* Custom Legend */}
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
              {type.name}: {breakdown[type.name]?.length || 0}
            </span>
          </div>
        ))}
      </div>

      {/* Pie Chart */}
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

      {/* Table for detailed results */}
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          margin: "20px 0",
        }}
      >
        <thead>
          <tr style={{ backgroundColor: "#f2f2f2", textAlign: "center" }}>
            <th style={{ padding: "8px", border: "1px solid #ddd" }}>
              Smell Type
            </th>
            <th style={{ padding: "8px", border: "1px solid #ddd" }}>
              File Path
            </th>
            <th style={{ padding: "8px", border: "1px solid #ddd" }}>
              Line Numbers
            </th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(breakdown).flatMap(([smellType, items]) =>
            items.map(({ file, lines }) => (
              <tr key={`${file}-${lines.join(",")}`}>
                <td style={{ padding: "8px", border: "1px solid #ddd" }}>
                  {smellType}
                </td>
                <td style={{ padding: "8px", border: "1px solid #ddd" }}>
                  {file}
                </td>
                <td style={{ padding: "8px", border: "1px solid #ddd" }}>
                  {lines.join(", ")}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Results;
