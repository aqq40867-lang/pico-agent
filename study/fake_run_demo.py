"""不需要 API key 的 pico 学习用 demo。

用 FakeModelClient 按剧本"扮演"模型，让你亲眼看到主循环每一步做了什么：
prompt 怎么拼、输出怎么解析、工具怎么被护栏拦下、trace/task_state 里记了什么。

用法（在仓库根目录）：
    uv run python study/fake_run_demo.py            # 默认场景 normal
    uv run python study/fake_run_demo.py malformed  # 模型输出坏 JSON -> retry
    uv run python study/fake_run_demo.py escape     # 路径逃逸 ../ -> 被拒绝
    uv run python study/fake_run_demo.py repeat     # 连续三次相同调用 -> 被拦
    uv run python study/fake_run_demo.py budget     # 工具步数耗尽 -> finalization 收尾
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pico.providers.clients import FakeModelClient  # noqa: E402
from pico.runtime import Pico, SessionStore  # noqa: E402
from pico.workspace import WorkspaceContext  # noqa: E402

READ = '<tool>{"name":"read_file","args":{"path":"hello.py"}}</tool>'
PATCH = '<tool name="patch_file" path="hello.py"><old_text>return a - b</old_text><new_text>return a + b</new_text></tool>'
FINAL = "<final>Fixed add(): it subtracted instead of adding.</final>"

SCENARIOS = {
    "normal": [READ, PATCH, FINAL],
    "malformed": [READ, "oops <tool>{not json}</tool>", PATCH, FINAL],
    "escape": ['<tool>{"name":"read_file","args":{"path":"../../secret.txt"}}</tool>', READ, PATCH, FINAL],
    "repeat": [READ, READ, READ, PATCH, FINAL],
    # max_steps=2：两次工具后预算耗尽，runtime 追加 "tool budget is exhausted" 提示再要一次 <final>
    "budget": [READ, PATCH, FINAL],
}


def main():
    scenario = sys.argv[1] if len(sys.argv) > 1 else "normal"
    outputs = SCENARIOS[scenario]
    repo = Path(tempfile.mkdtemp(prefix="pico-demo-"))
    (repo / "hello.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")

    model = FakeModelClient(outputs)
    agent = Pico(
        model_client=model,
        workspace=WorkspaceContext.build(repo),
        session_store=SessionStore(repo / ".pico" / "sessions"),
        approval_policy="auto",  # 跳过人工审批，方便演示
        max_steps=2 if scenario == "budget" else 6,
    )
    final = agent.ask("fix the bug in hello.py")

    print(f"=== scenario: {scenario}")
    print("FINAL ANSWER:", final)
    print("hello.py now:", (repo / "hello.py").read_text(encoding="utf-8").strip().splitlines()[-1])

    run_dir = agent.current_run_dir
    print("\n=== trace.jsonl（事件时间线）")
    keys = ("kind", "purpose", "name", "tool_status", "tool_error_code", "security_event_type", "trigger", "stop_reason")
    for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        print(f"  - {event['event']:<20}", {k: event[k] for k in keys if event.get(k)})

    print("\n=== task_state.json")
    print(json.dumps(json.loads((run_dir / "task_state.json").read_text(encoding="utf-8")), indent=2))

    print("\n=== 最后一次发给模型的 prompt（后半段）")
    print(model.prompts[-1][-1500:])
    print(f"\n工件目录: {run_dir}")


if __name__ == "__main__":
    main()
