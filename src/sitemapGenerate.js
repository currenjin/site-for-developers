require("babel-register")({
  presets: ["es2015", "react"],
});

const router = require("./sitemapRoutes").default;
const Sitemap = require("@snaddyvitch-dispenser/react-router-sitemap").default;

function generateSitemap() {
  return new Sitemap(router)
    .build("https://sfd.kro.kr")
    .save("./public/sitemap.xml");
}

generateSitemap();
