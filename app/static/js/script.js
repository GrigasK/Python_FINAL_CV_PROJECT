fetch("/database")
  .then((response) => response.json())
  .then((data) => {
    const skillsUpper = document.getElementById("skills");
    data.forEach((dataItem) => {
      console.log(dataItem);

      const skillsContainer = document.createElement("div");
      skillsContainer.className = "all-skills";

      const skillsTitleDiv = document.createElement("div");
      skillsTitleDiv.className = "wrapper";
      const skillsTitle = document.createElement("div");

      const skillsPercent = document.createElement("div");
      skillsPercent.textContent = dataItem[2] + "%";
      skillsPercent.style = "color: black;";

      skillsTitle.textContent = dataItem[1];
      skillsTitle.style = "font-weight: bold;";

      skillsTitleDiv.append(skillsTitle, skillsPercent);

      const skillsLevel = document.createElement("div");
      const skillBarOuter = document.createElement("div");
      skillBarOuter.className = "skills-bar-outer";

      const skillBarInner = document.createElement("div");
      skillBarInner.className = "skills-bar-inner";
      skillBarInner.style.width = dataItem[2] + "%";

      skillBarOuter.append(skillBarInner);
      skillsLevel.append(skillBarOuter);

      skillsContainer.append(skillsTitleDiv, skillsLevel);
      skillsUpper.append(skillsContainer);
    });
  })
  .catch((error) => console.error(error));
