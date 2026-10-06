# インシデント報告: ローカル git オブジェクトストアの消失（第 2 回、2026-10-06）

- 検知: 2026-10-06 10:11 JST（本セッション中）
- 対象: `C:\Users\kohak\programs\AEGIS`
- 影響: **`.git/refs/` ディレクトリと `.git/objects/pack/*.pack` が消失**。作業ツリーのファイルは無傷
- 現在の状態: **復旧済み**（`b5bbe0a3e7a3dc5ee14bbc66095d85fc043ef371` = `origin` の head まで）。
  作業ツリーは無傷（`git status` が「自分の編集 4 ファイルのみ」を示し、Temp に取った sha256 とも一致）
- 前回: `INCIDENT_2026-09-29_git-object-loss.md`（第 1 回。**同型** — 履歴オブジェクトの全消失、作業ツリーは無傷）

## 1. 何が起きたか（観測）

| 症状 | 実測 |
|---|---|
| `git status` | `fatal: not a git repository (or any of the parent directories): .git` |
| `git log`（ref 復元後） | `fatal: bad object HEAD` |
| `git cat-file -t <hash>` | 既知の**全**コミット（`b5bbe0a` / `1880d3ad` / `4958e4d` / `c22cbe15` / `cb2b5ad8`）で `could not get object info` |
| `.git/objects/pack/` | `multi-pack-index` と 3 つの **`.idx` のみ**。**`.pack` が 1 つも無い** |
| `.git/refs/` | **存在しない**（`.git/HEAD` は `ref: refs/heads/cf-grpc-and-goal-hygiene` のまま無傷） |
| `.git/logs/refs/` | **無傷**（`heads/cf-grpc-and-goal-hygiene` 42,659 B ほか） |

**引き金**: 直前に `git stash push -m cycle66-wip <4 files>` を実行し、ツールのタイムアウトで
**SIGTERM で中断**された。`git status` が壊れたのはその直後。**相関であって機序の証明ではない**
（第 1 回も `git stash` との相関が記録されている — 前回報告 §本文）。

**`.git/index` は無傷だったが汚染されていた** — 中断された stash がツリー全体を stage した状態で止まって
おり、ref を復元するまで `git status` は全ファイルを `A`（added）として報告した。オブジェクトが戻ると
汚染は自然に解消した（`--porcelain` が 5 行 → 4 行）。

## 2. 生存していたもの / 失われたもの

**生存**: 作業ツリーの全ファイル（**本サイクルの編集 4 ファイルを含む**。Temp へ取ったバックアップと
sha256 一致）／`.git/HEAD`・`.git/config`・`.git/index`／**`.git/logs/refs/` の reflog**（これが復旧の鍵）。

**失われた**:
- pack データ本体（**履歴オブジェクトの全体**）
- `refs/heads/cursor/cf-grpc-and-goal-hygiene` = `c22cbe158c878f77c1cd129ee71d857723acc5d2`
  — **ローカル専用**（`ls-remote` に無い）ため**復旧不能**。reflog に値だけが残った
- `refs/heads/dev` — reflog が **0 バイト**、remote にも対応物が無いため**値は不明**（**復旧不能**）

## 3. 復旧手順（実行したコマンド）

```sh
# 1. refs/ を戻す（これが無いと git は「リポジトリではない」と言う）
mkdir -p .git/refs/heads .git/refs/tags .git/refs/remotes/origin

# 2. reflog の最終行から ref を書く（reflog が唯一の正典）
#    refs/heads/cf-grpc-and-goal-hygiene  ← logs/refs/heads/… の最終行 = b5bbe0a
#    refs/heads/main / origin/*           ← git ls-remote origin（remote が正典）
printf 'b5bbe0a3e7a3dc5ee14bbc66095d85fc043ef371\n' > .git/refs/heads/cf-grpc-and-goal-hygiene
printf '1880d3ada80698090274c3831927a203b0dc0714\n' > .git/refs/heads/main
printf 'b5bbe0a3e7a3dc5ee14bbc66095d85fc043ef371\n' > .git/refs/remotes/origin/cf-grpc-and-goal-hygiene
printf '1880d3ada80698090274c3831927a203b0dc0714\n' > .git/refs/remotes/origin/main
printf 'ref: refs/remotes/origin/main\n' > .git/refs/remotes/origin/HEAD

# 3. 壊れたローカル専用 ref を外す（これが fetch を止める。§5）
rm -f .git/refs/heads/cursor/cf-grpc-and-goal-hygiene && rmdir .git/refs/heads/cursor

# 4. pack を取り戻す
GIT_TERMINAL_PROMPT=0 git fetch origin
```

**重要な落とし穴（実測）**: 手順 2 の後、`git fetch` は
`fatal: bad object refs/heads/cursor/cf-grpc-and-goal-hygiene` /
`error: … did not send all necessary objects` で**失敗した**。壊れた ref が 1 つあると
**fetch がストアを修復できない** — 「ref が壊れているのはストアが失われたから」という循環になる。
壊れたローカル専用 ref を外して初めて fetch が通った。

**`.git/refs/` は「緩い ref」で書く。** この `.git` には **`packed-refs` が無い**ので、
`.git/refs/` を失うと `git fetch` だけでは戻らない（fetch が書くのは `refs/remotes/*` のみで、
それは下記の深さ ≥ 2 の罠で消える）。**reflog から手で書くのが唯一の経路**。

## 4. 検証（4 経路が一致）

```
for-each-ref              refs/heads/cf-grpc-and-goal-hygiene b5bbe0a3… / refs/heads/main 1880d3ad…
                          refs/remotes/origin/{HEAD,cf-grpc-and-goal-hygiene,main}
git rev-parse @{u}        b5bbe0a3e7a3dc5ee14bbc66095d85fc043ef371
git rev-parse HEAD        b5bbe0a3e7a3dc5ee14bbc66095d85fc043ef371
git status -sb            ## cf-grpc-and-goal-hygiene...origin/cf-grpc-and-goal-hygiene（[gone] が消えた）
```

## 5. 第 1 回との関係 — 深さ ≥ 2 の ref 仮説と一致する

前回報告の **2026-10-01 追記**が、この `.git` 固有の失敗を記録している:

> `refs/` 下の**深さ ≥ 2** の `git update-ref` は **25/25 回** `rc=0`・stderr 空のまま
> **ref を書かず、囲むディレクトリを削除**した。**深さ ≤ 1** は **15/15 回**生存。

今回の観測はこの仮説と**整合する**:

- `refs/remotes/origin/cf-grpc-and-goal-hygiene` は `refs/` から**深さ 3**。本サイクルで
  `git fetch` の直後に **`refs/remotes/origin/` が再び消えた**（手で書いた直後にもかかわらず）。
  これは記録済みの「**B-6 は push のたびに `refs/remotes/origin/` を壊す**」と同じ形で、
  その正体がこの深さ ≥ 2 の失敗である可能性が高い。
- `refs/heads/cursor/cf-grpc-and-goal-hygiene` も**深さ 3**。`git stash` がこの ref に触れた
  （あるいは触れようとした）ことが、`refs/` 全体の消失と関係している可能性がある。

⚠️ **機序は依然として未確定**。前回報告のとおり、09-30 の測定はこの仮説を**反証**し、
10-01 の測定は**支持**している（**間欠的**）。したがってこれは**記録**であって、
確定した規則として扱ってはならない。

## 6. 実務上の規則（前回から変わらない）

1. **作業ツリーは失われない。** 失われるのは履歴オブジェクトと ref。だから**こまめに push する** —
   remote が唯一の復旧源になった（今回は `origin` に `b5bbe0a` があったので全損を免れた）。
2. **`.git/logs/refs/` を消さない。** それが ref の唯一の正典になる。
3. **入れ子 ref（`refs/` から深さ ≥ 2）はファイルへ直接書く。** `git update-ref` を使わない。
   今回の復旧もそうした（そして成功した）。
4. **壊れたローカル専用 ref は `git fetch` を止める。** ストアを修復する前に外す。
5. **`git stash` はこのリポジトリでは危険** — 第 1 回・第 2 回とも相関がある。4 ファイル程度なら
   `git diff > patch` のほうが安全（今回の復旧は Temp のバックアップで足りた）。

## 7. 追記（2026-10-06、サイクル 67 の push で再測定）

**B-6 は再発し、機序が一段はっきりした。** push（`4e973965..07802a08`）は成功したが、
`refs/remotes/` は **3 → 0** になった。そのあと `git fetch origin` は
`* [new branch] cf-grpc-and-goal-hygiene -> origin/cf-grpc-and-goal-hygiene` と
**成功を報告した**のに、`git for-each-ref refs/remotes/` は **0 のまま**、
`.git/refs/remotes/origin/` は**作られていなかった**（`FETCH_HEAD` だけが更新された）。
`remote.origin.fetch` は `+refs/heads/*:refs/remotes/origin/*` と**正しい**。

**bash からは作れる。** `mkdir -p .git/refs/remotes/origin` は成功し、`printf <sha> > …` で
書いた ref は `for-each-ref` に**見えた**。したがって規則 3 は `git update-ref` だけでなく
**`git fetch` にも及ぶ** — 「git 自身の ref 書き込みは入れ子ディレクトリを作れない」。
（git のプロセスと bash でサンドボックスが違う可能性があるが、**未確定**。）

**復旧手順（実測）**: `mkdir -p .git/refs/remotes/origin` → `origin/<branch>` に
`git ls-remote` の sha を、`origin/main` に main の sha を、`origin/HEAD` に
`ref: refs/remotes/origin/main` を書く。検証は `git for-each-ref refs/remotes/` が 3 件、
`git branch -r` が 3 行、`git status -sb` が `## <branch>...origin/<branch>`（ahead/behind 無し）。

⚠️ **push の検証は raw で行う — ただし Git Bash の `/tmp` は計器として使えない。**
`curl -o /tmp/x` の直後に、**別の呼び出し**で `wc -c < /tmp/x` を測ると **97945 B**（別の内容）を
返した。**Windows のパスに落とし、同じ呼び出しの中で測る**（正: 137437 B、blob と一致、cycle-67 の
文字列が 2 件）。sha 固定 URL とブランチ URL の両方で一致したので、CDN の遅延ではなく計器の誤り。
