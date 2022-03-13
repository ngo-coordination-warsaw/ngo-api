FROM golang:1.16 as builder

WORKDIR /app

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -v -installsuffix cgo ./cmd/ngo

FROM alpine:3.10

RUN apk update && apk add ca-certificates
RUN mkdir -p /app/migrations

COPY --from=builder /app/ngo /usr/bin/
COPY --from=builder /app/internal/ngo/storage/migrations /app/migrations

CMD ["ngo"]