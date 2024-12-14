import React from "react";
import { Chart, ArcElement, Tooltip } from "chart.js"; // Removed Legend since we're not using Chart.js's default legend
import { Pie } from "react-chartjs-2";

// Register Chart.js elements
Chart.register(ArcElement, Tooltip);

const Results = ({ results }) => {
  if (!results || !results.smell_breakdown || typeof results.total_smells !== "number") {
    return <div>No Results Yet</div>;
  }

  // Smell types and corresponding colors
  const smellTypes = [
    { name: "Large Class", color: "#ff6384" },
    { name: "Long Parameter List", color: "#36a2eb" },
    { name: "Long Method", color: "#cc65fe" },
    { name: "Long Message Chain", color: "#ffce56" },
    { name: "Long Base Class List", color: "#7cfc00" },
    { name: "Long Lambda Function", color: "#8a2be2" },
  ];

  // Extract raw counts
  const breakdown = results.smell_breakdown;

  // Calculate percentages
  const percentages = smellTypes.map((type) => {
    const count = breakdown[type.name] || 0; // Default to 0 if missing
    return ((count / results.total_smells) * 100).toFixed(1); // Percentage with 1 decimal place
  });

  // Prepare Pie chart data
  const data = {
    labels: smellTypes.map((type) => type.name),
    datasets: [
      {
        data: percentages.map((p) => parseFloat(p)), // Convert percentages to numbers
        backgroundColor: smellTypes.map((type) => type.color),
      },
    ],
  };

  return (
    <div>
      <h3>Total Smells Detected: {results.total_smells}</h3>
      {/* Custom Legend */}
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", marginBottom: "20px" }}>
        {smellTypes.map((type, index) => (
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
              {type.name}: {breakdown[type.name] || 0}
            </span>
          </div>
        ))}
      </div>
      {/* Pie Chart */}
      <div style={{ maxWidth: "400px", margin: "0 auto" }}>
        <Pie
          data={data}
          options={{
            plugins: {
              legend: {
                display: false, // Disable the default Pie chart legend
              },
              tooltip: {
                callbacks: {
                  // Tooltip shows percentage with 1 decimal place
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
    </div>
  );
};

export default Results;
