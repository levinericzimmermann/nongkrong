# import sys

from nongkrong.score import score

# sys.path.insert(0, "/sections")


sco = score.Score("TEST_SCORE", "sections/", "testSec")

if __name__ == "__main__":
    sco.render_notation()
    sco.render_sound()
