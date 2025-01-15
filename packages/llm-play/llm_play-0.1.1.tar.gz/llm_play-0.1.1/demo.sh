rm -rf demo
mkdir -p demo/prompts

cat <<EOF > demo/prompts/vanilla.md
Name a philosopher. Wrap your final answer with <answer></answer>
EOF

cat <<EOF > demo/prompts/cot.md
Name a philosopher. Think step-by-step. Wrap your final answer with <answer></answer>
EOF

uv run llm-play --prompt demo/prompts \
         --model qwen2.5-7b-instruct qwen2.5-14b-instruct \
         -t 1.5 \
         -n 3 \
         --output demo/samples

uv run llm-play --map demo/samples \
         --function __FIRST_TAGGED_ANSWER__ \
         --output demo/extracted

uv run llm-play --partition-globally demo/extracted \
         --relation "llm-play 'Are these two people from the same country: <person1>'%%CONDENSED_ESCAPED_DATA1%%'</person1> and <person2>'%%CONDENSED_ESCAPED_DATA2%%'</person2>?' --model qwen2.5-72b-instruct --predicate" \
         --output demo/result.csv
