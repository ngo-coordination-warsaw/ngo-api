package ngo

import (
	"time"

	"github.com/sirupsen/logrus"
)

type airtableData struct {
	ID     string
	Fields map[string]interface{}
}

func (ngo *ngo) loadAirtable() {
	loaders := map[string]func() error{
		"data":           ngo.loadData,
		"categoriesData": ngo.loadCategories,
		"adminsData":     ngo.loadAdmins,
	}

	for k, l := range loaders {
		logrus.Infof("Loading %s", k)

		err := l()
		if err != nil {
			logrus.Errorf("Loader err: %s", err.Error)
		}

		time.Sleep(time.Second)
	}
}

type org struct {
	Name            string
	NameUA          string
	Address         string
	Category        []string
	CategoryName    []string
	Phone           string
	PhoneAdditional string
	Email           string
	Description     string
	DescriptionUA   string
	//PrivateInfo     string
}

func (ngo *ngo) loadData() error {
	type organization struct {
		Fields org
	}

	orgs := []organization{}
	if err := ngo.airtable.ListRecords(ngo.config.AirtableOrganizationsTable, &orgs); err != nil {
		return err
	}

	organizationsData := make(map[string][]org)
	for _, o := range orgs {
		for _, c := range o.Fields.Category {
			if _, ok := organizationsData[c]; !ok {
				organizationsData[c] = []org{}
			}

			organizationsData[c] = append(organizationsData[c], o.Fields)
		}
	}

	ngo.organizationsData = organizationsData

	return nil
}

func (ngo *ngo) loadAdmins() error {
	admins := []airtableData{}
	if err := ngo.airtable.ListRecords(ngo.config.AirtableAdminsTable, &admins); err != nil {
		return err
	}

	adminsParsed := make(map[string]struct{})
	for _, a := range admins {
		adminsParsed[a.Fields["Name"].(string)] = struct{}{}
	}

	ngo.adminsData = adminsParsed

	return nil
}

func (ngo *ngo) loadCategories() error {
	data := []airtableData{}
	if err := ngo.airtable.ListRecords(ngo.config.AirtableCategoriesTable, &data); err != nil {
		return err
	}

	cat := []interface{}{}
	for _, i := range data {
		cat = append(cat, map[string]interface{}{
			"ID":     i.ID,
			"Name":   i.Fields["Name"],
			"NameUA": i.Fields["NameUA"],
		})
	}

	ngo.categoriesData = cat

	return nil
}
