package sample

import (
	"context"
	"net/http"
)

func Handle(w http.ResponseWriter, r *http.Request) {
	context.Background()
}

func Library() {
	panic("boom")
}
