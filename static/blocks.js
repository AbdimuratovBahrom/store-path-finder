 
    const tooltip = document.getElementById("tooltip");
    const areas = document.querySelectorAll("area");

    areas.forEach(area => {
      area.addEventListener("mouseenter", () => {
        tooltip.style.display = "block";
        tooltip.innerText = area.dataset.tooltip;
      });
      area.addEventListener("mousemove", e => {
        tooltip.style.left = e.pageX + 12 + "px";
        tooltip.style.top = e.pageY + 12 + "px";
      });
      area.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
      });
    });
  