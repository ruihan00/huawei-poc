"use client";

export default function Box({x1, y1, x2, y2}) {
  const style = {
    position: "absolute",
    border: "3px solid blue",
    left: x1,
    top: y1,
    width: x2 - x1,
    height: y2 - y1,
  };
  return (
    <div
      className="rectangle"
      style={style}
    />
  );
}
