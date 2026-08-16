FROM golang:1.24 AS build
WORKDIR /src
COPY backend/go.mod backend/go.sum ./
RUN go mod download
COPY backend/ ./
RUN go test ./... && \
    CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags='-s -w' -o /out/xkjy-api ./cmd/api && \
    CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags='-s -w' -o /out/xkjy-migrate ./cmd/migrate && \
    CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags='-s -w' -o /out/xkjy-healthcheck ./cmd/healthcheck

FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /app
COPY --from=build /out/xkjy-api /app/xkjy-api
COPY --from=build /out/xkjy-migrate /app/xkjy-migrate
COPY --from=build /out/xkjy-healthcheck /app/xkjy-healthcheck
COPY backend/migrations /app/migrations
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/app/xkjy-api"]
