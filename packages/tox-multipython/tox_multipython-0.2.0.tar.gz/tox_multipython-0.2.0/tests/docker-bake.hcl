variable "CASES_TOX3" {
  default = [
    {tag="py314t", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py314t", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py314t", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py313t", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py313t", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py313t", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py314", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py314", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py314", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py313", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20"},
    {tag="py313", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.27"},
    {tag="py313", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py312", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py312", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py312", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py311", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py311", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py311", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py310", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py310", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py310", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py39", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py39", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py39", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py38", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38", fail="py37 py36 py35 py27", venv=">=20"},
    {tag="py38", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py38", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py37", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20"},
    {tag="py37", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", fail="py36 py35 py27", venv=">=20,<20.27"},
    {tag="py37", pass="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37 py36 py35 py27", fail="", venv=">=20,<20.22"},

    {tag="py36", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20"},
    {tag="py36", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20,<20.27"},
    {tag="py36", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20,<20.22"},

    {tag="py35", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20"},
    {tag="py35", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20,<20.27"},
    {tag="py35", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20,<20.22"},

    {tag="py27", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20"},
    {tag="py27", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20,<20.27"},
    {tag="py27", fail="py314t py313t py314 py313 py312", pass="py311 py310 py39 py38 py37 py36 py35 py27", venv=">=20,<20.22"},
  ]
}

group "default" {
  targets = ["tox3"]
}

target "tox3" {
  dockerfile = "tests/Dockerfile"
  context = "."
  args = {
    CASE_NAME = "${CASE["tag"]} ${CASE["venv"]}",
    PYTHON_TAG = CASE["tag"],
    TAGS_PASSING = CASE["pass"],
    TAGS_FAILING = CASE["fail"],
    TAGS_NOTFOUND = "py20",  # always missing in multipython
    VIRTUALENV_PIN = CASE["venv"],
  }
  matrix = {
    CASE = CASES_TOX3
  }
  name = "test_tox3_${CASE["tag"]}_${regex_replace(CASE["venv"], "[^0-9]", "_")}"
  output = ["type=cacheonly"]
}
