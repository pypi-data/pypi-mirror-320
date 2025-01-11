variable "CASES" {
  default = {
    py314t = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py313t = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py314 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py313 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py312 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py311 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py310 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py39 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py38 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38", invalid="py37 py36 py35 py27"},
    py37 = {passing="py314t py313t py314 py313 py312 py311 py310 py39 py38 py37", invalid="py36 py35 py27"},
    py36 = {invalid="py314t py313t py314 py313 py312", passing="py311 py310 py39 py38 py37 py36 py35 py27"},
    py35 = {invalid="py314t py313t py314 py313 py312", passing="py311 py310 py39 py38 py37 py36 py35 py27"},
    py27 = {invalid="py314t py313t py314 py313 py312", passing="py311 py310 py39 py38 py37 py36 py35 py27"},
  }
}

target "default" {
  dockerfile = "tests/Dockerfile"
  context = "."
  args = {
    TOX_TAG = CASE,
    TAGS_PASSING = CASES[CASE]["passing"],
    TAGS_INVALID = CASES[CASE]["invalid"],
    TAGS_NOTFOUND = "py20",  # always missing in multipython
  }
  matrix = { CASE = keys(CASES) }
  name = "test_${CASE}"
  output = ["type=cacheonly"]
}
