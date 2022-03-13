package types

import (
	"github.com/joho/godotenv"
	"github.com/kelseyhightower/envconfig"
	"github.com/pkg/errors"
)

type Config struct {
	AirtableApiKey             string `required:"true" split_words:"true"`
	AirtableBaseID             string `required:"true" split_words:"true"`
	AirtableOrganizationsTable string `required:"true" split_words:"true"`
	AirtableAdminsTable        string `required:"true" split_words:"true"`
	AirtableCategoriesTable    string `required:"true" split_words:"true"`

	HttpPort uint `required:"true" split_words:"true" default:"8080"`
}

func InitConfig(cfg interface{}, envFile string) error {
	if envFile != "" {
		err := godotenv.Load(envFile)
		if err != nil {
			return errors.Wrap(err, "error loading env file")
		}
	}

	err := envconfig.Process("", cfg)
	if err != nil {
		return errors.Wrap(err, "envconfig")
	}

	return nil
}
