package ngo

import (
	"fmt"
	"io"

	//"github.com/dgrijalva/jwt-go"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"

	"github.com/ngo-coordination-warsaw/ngo-api/internal/pkg/http/response"
	"github.com/ngo-coordination-warsaw/ngo-api/internal/pkg/types"
)

func (ctrl *ngo) ServeAPI() error {
	r := gin.Default()
	r.Use(cors.New(cors.Config{
		AllowAllOrigins:  true,
		AllowMethods:     []string{"GET", "POST", "PUT", "HEAD", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Length", "Content-Type", "Authorization", "Accept-Encoding"},
		AllowCredentials: true,
	}))

	r.NoRoute(func(c *gin.Context) {
		c.JSON(404, gin.H{"code": "PAGE_NOT_FOUND", "message": "Page not found"})
	})

	rg := r.Group("/")

	rg.GET("/data/:category", ctrl.getData)
	rg.GET("/categories", ctrl.getCategories)

	log.Infof("Starting API on port %d", ctrl.config.HttpPort)
	return r.Run(fmt.Sprintf(":%d", ctrl.config.HttpPort))
}

func parseParams(c *gin.Context, params interface{}) error {
	err := c.ShouldBindJSON(&params)
	if err != nil && err == io.EOF {
		err = types.ErrEmptyParams
	}

	return err
}

func (ngo *ngo) getCategories(c *gin.Context) {
	response.Success().SetData(gin.H{
		"categoriesData": ngo.categoriesData,
	}).Send(c)
}

func (ngo *ngo) getData(c *gin.Context) {
	cat := c.Param("category")

	response.Success().SetData(gin.H{
		"orgs": ngo.organizationsData[cat],
	}).Send(c)
}
