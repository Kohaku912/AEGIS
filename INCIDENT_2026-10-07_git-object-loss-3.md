# インシデント報告: ローカル git オブジェクトストアの消失（第 3 回、2026-10-07）

- 検知: 2026-10-07 17:58 JST（本セッション中、サイクル 92）
- 対象: `C:\Users\kohak\programs\AEGIS`
- 影響: **`.git/refs/heads/`・`.git/logs/`・`.git/packed-refs` と `.git/objects/pack/*.pack` が消失**。作業ツリーは無傷
- 現在の状態: **復旧済み**（`4f812423a871f6bdbc6cd7c12cea33afe4de38b4` = `origin` の `cf-grpc-and-goal-hygiene`）。
  `git fsck --connectivity-only` が**無出力で exit 0**、`git count-objects -vH` が `garbage: 0`
- 前回: 第 1 回（`INCIDENT_2026-09-29_git-object-loss.md`）／第 2 回（`INCIDENT_2026-10-06_git-object-loss-2.md`）と**同型**

## 1. 何が起きたか（観測）

**観測の入口**: `git stash push -- scripts/audit-production-readiness.py` が
`fatal: 19c4a5b4d9342d2429727d0d103daec1b930dca9 is not a valid object` で**即座に失敗**し、
git が壊れていることが分かった。**第 1 回・第 2 回と同じく `git stash` の呼び出しと相関している**（§6 規則 5）。

⚠️ **ただし今回は stash が「原因」ではなく「検知器」である可能性がある。** 失敗メッセージは
*「そのオブジェクトが既に無い」* ことを意味しており、stash が**読みに行って初めて気づいた**形だからである。
壊れる **2 分前**（17:56）には同じセッションで `git show HEAD:scripts/audit-production-readiness.py` が
成功していたので、その間に何かがストアを消した — それが stash 自身なのか、stash 以外の何かなのかは
**区別できていない**。**機序は依然として未確定**であり、以下は相関の記録である。

| 症状 | 実測 |
|---|---|
| `git stash push -- <path>` | `fatal: 19c4a5b4… is not a valid object` |
| `git rev-parse HEAD` | `fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree.` |
| `git cat-file -t 4f812423…`（直前に `git show HEAD:` が読めていた commit） | `fatal: git cat-file: could not get object info` |
| `.git/refs/heads/` | **存在しない**（`.git/HEAD` は `ref: refs/heads/cf-grpc-and-goal-hygiene` のまま無傷） |
| `.git/refs/remotes/origin/` | **存在するが空**（ファイル 0 件） |
| `.git/logs/` | **存在しない** |
| `.git/packed-refs` | **存在しない** |
| `.git/objects/` の緩いオブジェクト | **0 個** |
| `.git/objects/pack/` | `multi-pack-index` と **`.idx` 1 個のみ**。**`.pack` が無い** |
| `.git/index` | **無傷**（152,429 B、全ファイルを保持） |

⚠️ **第 2 回との差**: 今回は **reflog も消えた**。第 2 回は `.git/logs/refs/` が「ref の唯一の正典」として
復旧の鍵になったが、今回はその経路が無い。**remote と `.git/index` だけが残った。**

**壊れる直前まで git は正常だった。** 同じセッションで `git show HEAD:scripts/audit-production-readiness.py`
が成功し、`grep` が `.git/logs/HEAD` の 341 行目（サイクル 91 のコミット）を読めていた。**数分で消えた。**

## 2. 生存していたもの / 失われたもの

**生存**: 作業ツリーの全ファイル（**サイクル 92 の未コミット編集を含む**）／`.git/HEAD`・`.git/config`・
`.git/index`／remote 上の全履歴（`origin` に `4f812423` があった）。

**失われた**: pack データ本体（履歴オブジェクトの全体）／`refs/heads/cf-grpc-and-goal-hygiene`／
`refs/remotes/*`／`.git/logs/`（reflog 全体）／`packed-refs`。
**今回はローカル専用 ref が無かった**ので、第 2 回のような「復旧不能な ref」は生じていない。

## 3. 復旧手順（実行したコマンド）

```sh
# 1. remote が正典。壊れたローカル専用 ref が無いので fetch は一発で通った（第 2 回 §3 の落とし穴は今回は非該当）
GIT_TERMINAL_PROMPT=0 git fetch origin
#   -> * [new branch] cf-grpc-and-goal-hygiene -> origin/cf-grpc-and-goal-hygiene
#      * [new branch] main                      -> origin/main

# 2. HEAD が指す ref を戻す。refs/heads/<branch> は **深さ 1** なので git update-ref で書ける
#    （第 2 回の「深さ >= 2 は git 自身が書けない」仮説と整合する）
git update-ref refs/heads/cf-grpc-and-goal-hygiene 4f812423a871f6bdbc6cd7c12cea33afe4de38b4

# 3. 検証
git rev-parse HEAD          # 4f812423a871f6bdbc6cd7c12cea33afe4de38b4
git status --short          # 自分の編集 2 件のみ（M 1 / ?? 1）
git --no-pager diff --stat  # 1 file changed, 31 insertions(+), 1 deletion(-)
```

**`git checkout` を使わなかった。** `git checkout -B <branch> origin/<branch>` は作業ツリーと index を
上書きするので、**未コミットの編集が唯一のコピー**である瞬間に使ってはならない。

## 4. 復旧後の後始末 — 残骸が `git fsck` を壊していた（今回の新規知見）

fetch は新しい pack（`pack-3bec4da7…`、219,110,954 B、13,454 オブジェクト）を落としたが、
**古い `multi-pack-index`（09-29）と、対応する `.pack` を失った孤児 `.idx`（`pack-f19ae93f….idx`）が残った**。

| 症状 | 実測 |
|---|---|
| `git count-objects -vH` | `garbage: 1` / `size-garbage: 361.33 KiB`、stderr に `warning: no corresponding .pack: …pack-f19ae93f….idx` |
| `git fsck --connectivity-only` | `failed to load pack in position 0` / `in position 1`、続けて `failed to load pack entry for oid[…]=…` が**大量** |
| `git multi-pack-index write` | `error: could not load pack 0`（**古い MID を読もうとして失敗する**） |

**修復**（`.git/objects/pack/` の派生キャッシュを退避して作り直す。pack 本体には触らない）:

```sh
mv .git/objects/pack/multi-pack-index <退避先>/multi-pack-index.stale
mv .git/objects/pack/pack-f19ae93f….idx  <退避先>/
git multi-pack-index write     # 現存する pack だけを指す MID を再生成
```

**結果**: `git fsck --connectivity-only` が**無出力・exit 0**、`git count-objects -vH` が
`in-pack: 13454 / packs: 1 / garbage: 0`。
⚠️ **古い MID を退避せずに `multi-pack-index write` を先に叩くと失敗する**（順序が要る）。

## 5. 計器としての `.git/index`（今回の新規知見）

`.git/index` が無傷だったので、**「作業ツリーの編集が本当に意図した差分だけか」を履歴に頼らず測れた**:

```sh
git ls-files -s scripts/audit-production-readiness.py   # 100644 1103dd75… 0   <- index が持つ HEAD の blob
git hash-object <壊れる直前に git show HEAD:… で保存したスナップショット>   # 1103dd75…  == index と一致
git hash-object scripts/audit-production-readiness.py                      # 11e12e48…  != index
diff -u <スナップショット> scripts/audit-production-readiness.py            # _result_cause の追加のみ
```

**「壊れる直前に `git show HEAD:<path>` を控えておく」が効いた。** 履歴が消えても、index の blob sha と
突き合わせれば**未コミット差分の正体**を確定できる。

## 6. 実務上の規則（第 2 回から 1 つ昇格）

1. **作業ツリーは失われない。** 失われるのは履歴オブジェクトと ref。**こまめに push する** —
   3 回とも remote が唯一の復旧源だった。
2. **`.git/logs/` を消さない／当てにしない。** 第 2 回は reflog が正典だったが、**今回は reflog ごと消えた**。
   したがって reflog は「あれば嬉しい」であって、**正典は常に remote**。
3. **入れ子 ref（`refs/` から深さ >= 2）はファイルへ直接書く。** `git update-ref` を使わない
   （`refs/heads/<branch>` は深さ 1 なので可）。
4. **壊れたローカル専用 ref は `git fetch` を止める。** ストアを修復する前に外す。
5. ⚠️ **`git stash` をこのリポジトリで使ってはならない。** **3 回のオブジェクトストア消失すべてで
   `git stash` の呼び出しが同じセッションにあった**（第 1 回は `push`/`pop` の対、第 2 回は SIGTERM 中断、
   今回は `fatal: … is not a valid object` で即失敗）ので、**その意味で 3/3 が相関している**。
   ⚠️ **機序は依然として未確定** — 今回は stash が原因ではなく**検知器**である可能性がある（§1）。
   したがってこれは「危険と**相関する**道具を避ける」規則であって、**原因の断定ではない**。
   **数ファイルなら `git diff > patch` か Temp への `cp` で足りる**（今回は Temp のコピーで足りた）。
   未コミットの編集を守る手段として `git stash` を選ばない。
6. **復旧後は `git fsck --connectivity-only` と `git count-objects -vH` を測る。** `garbage > 0` や
   `failed to load pack` は**残骸**のサインで、放置すると後続の操作が間欠的に失敗する。
