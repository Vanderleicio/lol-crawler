from extractors.golgg_extractor import GolggExtractor
from core.config import URLS

if __name__ == "__main__":
    extrator = GolggExtractor(URLS['golgg'])
    ligas = extrator.extract()