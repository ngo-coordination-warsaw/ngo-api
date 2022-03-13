package response

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type Response struct {
	Status  int    `json:"status"`
	Message string `json:"message"`
	Data    gin.H  `json:"data"`
}

func Success() *Response {
	r := &Response{}
	r.Status = http.StatusOK
	r.Message = http.StatusText(r.Status)
	return r
}

func BadRequest() *Response {
	r := &Response{}
	r.Status = http.StatusBadRequest
	r.Message = http.StatusText(r.Status)
	return r
}

func Unauthorized() *Response {
	r := &Response{}
	r.Status = http.StatusUnauthorized
	r.Message = http.StatusText(r.Status)
	return r
}

func InternalError() *Response {
	r := &Response{}
	r.Status = http.StatusInternalServerError
	r.Message = http.StatusText(r.Status)
	return r
}

func (r *Response) SetMessage(msg string) *Response {
	r.Message = msg
	return r
}

func (r *Response) SetData(data gin.H) *Response {
	r.Data = data
	return r
}

func (r *Response) Send(ctx *gin.Context) {
	ctx.JSON(r.Status, r)
}
