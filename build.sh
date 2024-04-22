echo "const hitop_mappings = $(cat data/hitop-mappings.json | jq --compact-output .);"
echo "const hitop_sr = $(cat data/hitop-sr.json | jq --compact-output .);"
echo "const whodas_full = $(cat data/whodas-full.json | jq --compact-output .);"
echo "const whodas_short = $(cat data/whodas-short.json | jq --compact-output .);"