const fs = require('fs');

function generateMarkdown(categories, sites) {
  let markdown = '';
  categories.forEach(category => {
    markdown += `## ${category.text}\n`;
    const categorySites = sites.filter(site => site.categories.includes(category.category));
    categorySites.forEach(site => {
      markdown += `- [${site.name}](${site.link}) - ${site.description}\n`;
    });
  });
  return markdown;
}

const categories = require('../../categories.yml');
const sites = require('../../sites.yml');

const readmeContent = generateMarkdown(categories, sites);
fs.writeFileSync('../../README.md', readmeContent);
