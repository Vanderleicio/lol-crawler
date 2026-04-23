from .golgg_extractor import GolggExtractor


class ExtractorFactory:
    @staticmethod
    def get_extractor(url):
        if "gol.gg" in url:
            return GolggExtractor()
        else:
            raise ValueError("URL não suportada ainda.")