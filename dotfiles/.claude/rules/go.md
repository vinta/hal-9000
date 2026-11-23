---
paths:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.work"
---

# Go

When an older and a newer idiom both fit the module's `go` line, pick the newer one: training data holds more old Go than new.

## Tooling

- Format with `golangci-lint fmt` when the project's config enables formatters. Run `go test -race ./...`.
- After writing code, run `go fix -diff` on the packages you changed (`./internal/auth`, not `./...`), then apply it, until it reports nothing, and build again after. Keep its fixes in files you changed; report fixes in other files instead of keeping them. A whole-module `go fix ./...` is its own commit, run only when asked.
- Run tools under the toolchain the `go` line selects (leave `GOTOOLCHAIN` at its default), so a `go 1.27` module gets 1.27's vet and `go fix`.
- Lint with `golangci-lint run` when the project has a `.golangci.yml`, using a binary install (Homebrew), not `go get -tool`.
- Pin other Go-built dev tools with `go get -tool <pkg>@<version>` and run them as `go tool <name>`; no `tools.go` blank-import file.
- Run `govulncheck ./...` after dependency changes when the project uses it.

## Go 1.27 (only when the `go` line is 1.27 or later)

- Give a type a generic method (`func (s Set[T]) Map[U any](f func(T) U) []U`) when the operation belongs to that type, and a package-level generic function when it does not. A method that must satisfy an interface cannot be generic.
- Use `encoding/json/v2` for new JSON code, and give custom types `MarshalJSONTo`/`UnmarshalJSONFrom` methods instead of `MarshalJSON`/`UnmarshalJSON`. Choose explicitly where v2's defaults leave a gap: `json.Deterministic(true)` when output must be byte-stable (golden files, hashes, signatures); an explicit encoding for `time.Duration` fields (`jsonv1.FormatDurationAsNano(true)` or a custom type), which v2 rejects otherwise; a `case:ignore` tag on fields that must match input case-insensitively; an `embed` field of type `jsontext.Value` to keep unknown members.
- Leave existing `encoding/json` code on v1 unless asked to migrate: v1 stays supported, and v2 changes output (nil slices as `[]`, map order, byte arrays as Base64, HTML escaping). To migrate, switch call sites to v2 with `jsonv1.DefaultOptionsV1()` first, then append v2 overrides after it (`json.FormatNilSliceAsNull(false)`; later options win), checking output at each step.
- Use the standard `uuid` package (`uuid.New()`, `uuid.NewV7()` for time-ordered IDs, `uuid.Parse`) instead of `github.com/google/uuid`.
- Use `strings.CutLast`/`bytes.CutLast` instead of `LastIndex` plus slicing, and `url.URL.Clone`/`url.Values.Clone` instead of manual copies.
- Set promoted fields directly in keyed struct literals: `Document{CreatedBy: "alice", Name: "r.pdf"}`, not `Document{AuditInfo: AuditInfo{CreatedBy: "alice"}, ...}`.
- Close an HTTP response body with `defer resp.Body.Close()` and no `io.Copy(io.Discard, resp.Body)` drain; share one `http.Client` instead of one per request.
- In `synctest` tests, use `synctest.Sleep(d)` instead of `time.Sleep(d)` followed by `synctest.Wait()`, and `httptest.NewTestServer` instead of a real listener.

## Go 1.26

- Get a pointer to a value with `new(expr)`: `new(true)`, `new(30 * time.Second)`, instead of a `ptr[T]` helper or a temporary used only for `&v`. Convert untyped constants to the field's type: `new(int32(30))`, since `new(30)` is `*int`.
- Match error types with `if pe, ok := errors.AsType[*fs.PathError](err); ok`, not `errors.As` with a target variable.
- Make crypto tests deterministic with `testing/cryptotest.SetGlobalRandom`, not a custom `rand` reader.
- Use `httputil.ReverseProxy.Rewrite`, not `Director`.

## Earlier releases

- `cmp.Or(a, b, "default")` for a fallback chain, except when a later argument is costly or has side effects (all are evaluated) or when a zero value is a valid result.
- `slices.SortFunc` with `cmp.Compare` instead of `sort.Slice`; `slices.SortStableFunc` where order of equal elements matters.
- `slices.Sorted(maps.Keys(m))`, `slices.Collect`, `slices.Index`/`IndexFunc`/`Max`/`Min`/`Reverse`, `maps.Clone`, `maps.DeleteFunc` and `clear` instead of hand loops.
- `sync.OnceValue`/`OnceFunc` instead of `sync.Once` plus a variable; `context.AfterFunc` instead of a goroutine waiting on `ctx.Done()`; `context.WithCancelCause`/`WithTimeoutCause` when callers need to know why.
- `errors.Join` to combine errors; `errors.Is`, never `==`, for sentinels.
- `mux.HandleFunc("GET /items/{id}", h)` with `r.PathValue("id")` instead of manual method checks and path trimming.
- `testing/synctest.Test` for code that uses time, timers or tickers, never `time.Sleep` in tests; use `net.Pipe`, not real sockets, inside the bubble.
- `b.Loop()` in benchmarks. `t.Context()` in tests, but a fresh context in `t.Cleanup` functions.
- `log/slog` for logs, `os.Root` to confine file access to one directory.
- No `automaxprocs` and no explicit `GOMAXPROCS`: leave CPU sizing to the runtime.

## Style

- Don't repeat the package name in its identifiers (`config.Load`, not `config.LoadConfig`).
- Define an interface in the package that consumes it, small, once a second implementation or a test needs it. Accept interfaces, return concrete types. No interface per struct (`UserService` beside `userService`).
- Check `err` before touching any other return value. Check `scanner.Err()` after the loop.
- Wrap with context, lowercase, no "failed to": `fmt.Errorf("load config: %w", err)`. Use `%w` only when callers need `errors.Is`/`As` on the cause, `%v` to keep it out of your API. Handle an error once: log it or return it, never both.
- `ctx context.Context` is the first parameter; never store it in a struct.
- Prefer synchronous APIs and let the caller add concurrency. Every goroutine has an owner that waits for it and a way to stop. Only the sender closes a channel. Use `errgroup` for fan-out that returns errors. Use a mutex for shared state and a channel for handing off work; never copy a struct that holds a mutex.
- Tests follow the assertion style the project already uses. Otherwise: table-driven with `t.Run` and named cases; compare structs with `cmp.Diff(want, got)` from go-cmp, not `reflect.DeepEqual`; call `t.Helper()` in helpers; never `t.Fatal` from a goroutine the test spawned.
- Receivers are one or two letters. No `Get` prefix on getters.
- Declare an empty slice as `var s []T` and test `len(s) == 0`, except where `encoding/json` v1 output must be `[]`, not `null`.
- Use an options struct when most callers set options; functional options only for many rarely used settings.
- `main` calls `run() error` and is the only place that calls `os.Exit` or `log.Fatal`.
