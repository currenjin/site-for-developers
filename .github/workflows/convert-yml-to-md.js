const fs = require('fs');
const yaml = require('js-yaml');

const initContent = `
## 어떤 저장소인가요?
- 개발자가 참고하면 좋은 대표적인 사이트를 모아놓은 북마크 저장소입니다. 한 분 한 분에게 도움이 되었으면 좋겠습니다. 🙏🏾
- 또한, 참고하면 좋겠다고 생각되는 사이트는 \`Pull Request\` 로 참여해 주시면 감사하겠습니다! -> [How to contribute](./HOW-TO-CONTRIBUTE.md)

## 기여자
[![author](https://img.shields.io/badge/author-currenjin-green.svg?style=flat-square)](https://currenjin.github.io/resume)

<a href="https://github.com/currenjin/site-for-developers/graphs/contributors"><img src="https://opencollective.com/site-for-developers/contributors.svg?width=720"></a>

## 북마크
`;

function generateMarkdown(categories, sites) {
  let markdown = initContent;

  categories.forEach((category, index) => {
    const categoryName = category.text;
    const depth = index + 2;

    markdown += `${'#'.repeat(depth)} ${categoryName}\n`;

    const categorySites = sites.filter(site => site.categories.includes(category.category));
    categorySites.forEach(site => {
      const { name, link, description } = site;
      markdown += `${'#'.repeat(depth + 1)} [${name}](${link}) - ${description}\n`;
    });

    markdown += '\n';
  });

  return markdown;
}

const categoriesContent = fs.readFileSync('./categories.yml', 'utf-8');
const categories = yaml.load(categoriesContent);

const sitesContent = fs.readFileSync('./sites.yml', 'utf-8');
const sites = yaml.load(sitesContent);

const generatedMarkdown = generateMarkdown(categories, sites);

fs.writeFileSync('./README.md', generatedMarkdown, 'utf8');

