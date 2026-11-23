# claude-statusline

Claude Code のステータスラインに、モデル名、effort、git のブランチ、コンテキストの使用率、5 時間と 7 日の使用量を 1 行で出すスクリプトです。

```text
 Opus 5.5 high │ ⎇ main │ ctx ███▋░░░░░░ 37% │ 5h █▏░░░░░░░░ 12% │ 7d ██████▉░░░ 69%
```

- モデル名の後ろに effort を出し、low は緑、max は赤のように段階ごとに色を変える
- 使用率のバーは、0% で緑、50% で黄、100% で赤になるように色が移る。1 マスを 8 段階に分けて描く
- Claude Code から値が渡されない項目は出さない。git の管理外のディレクトリでは、ブランチを出さない

## 必要なもの

- Python 3
- git
- 24 ビットカラー（truecolor）に対応したターミナル

## 入れ方

`statusline.py` を `~/.claude/statusline.py` に置き、実行権限を付けます。

```bash
curl -fsSL https://raw.githubusercontent.com/shnaka/claude-statusline/main/statusline.py -o ~/.claude/statusline.py
chmod +x ~/.claude/statusline.py
```

`~/.claude/settings.json` に次の設定を足します。

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
}
```

## 使用量のファイル

描画のたびに、5 時間と 7 日の使用量を `~/.claude/cache/rate-limits.json` に保存します。ステータスラインの外にあるスクリプトや Claude のセッションから使用量を読めるようにするためです。たとえば、CLAUDE.md に「5 時間の使用量が 90% を超えたら作業を止める」と決めておくと、Claude がこのファイルを読んで判断できます。

```json
{"rate_limits": {"five_hour": {"used_percentage": 12}, "seven_day": {"used_percentage": 68.9}}, "updated_at": 1795403932.44}
```

- 使用量はアカウント単位なので、どのセッションが保存しても同じ値になる
- `updated_at` は保存した時刻（UNIX 時刻）。ステータスラインが描画されないあいだは更新されないので、読む側で古さを確かめる

```bash
python3 -c "import json,os,time;d=json.load(open(os.path.expanduser('~/.claude/cache/rate-limits.json')));print(d['rate_limits']['five_hour']['used_percentage'], int(time.time()-d['updated_at']), 'sec ago')"
```
