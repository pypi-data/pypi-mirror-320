#!/usr/bin/env bash


REPO="https://raw.githubusercontent.com/makukha/multipython"
TAGS="$(
  curl -s "$REPO/refs/heads/main/tests/share/info/unsafe.json" \
  | jq -r '.python[] | .tag' \
  | nl -w2 -s' '
)"


sort_cells () {
  sed 's/ /\n/g' <<<"$1" | while IFS= read -r CELL
  do
    TAG="$(cut -d= -f1 <<<"$CELL")"
    INDEX="$(sed -n 's/^\([ ]*[^ ][^ ]*\) '"$TAG"'$/\1/p' <<<"$TAGS")"
    printf '%s %s\n' "$INDEX" "$CELL"
  done | sort | cut -c 4- | xargs
}

print_rows () {
  while IFS= read -r JSON
  do
    TAG="$(jq -r '.TOX_TAG' <<<"$JSON")"
    PASSING="$(jq -r '.TAGS_PASSING' <<<"$JSON")"
    INVALID="$(jq -r '.TAGS_INVALID' <<<"$JSON")"
    INDEX="$(sed -n 's/^\([ ]*[^ ][^ ]*\) '"$TAG"'$/\1/p' <<<"$TAGS")"
    ROW="$(sed 's/ /=P /g' <<<"$PASSING ") $(sed 's/ /=I /g' <<<"$INVALID ")"
    printf '%s %s %s\n' "$INDEX" "$TAG" "$(sort_cells "$ROW")"
  done | sort | cut -c 4-
}

format_row () {
  sed '
    s|^\([^ ][^ ]*\) |<tr><th><code>\1</code></th> |;
    s| \([^ ]*\)=P| <td>✅</td>|g;
    s| \([^ ]*\)=I| <td>🚫</td>|g;
    s|$|</tr>|;
  '
}

docker buildx bake -f tests/docker-bake.hcl --print 2>/dev/null \
  | jq -rc '.target[].args' \
  | print_rows | format_row
