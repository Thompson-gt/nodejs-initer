package Generator

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sync"
)

// enum holding all of the options for the colors
const (
	rED_COLOR Color = iota
	gREEN_COLOR
	yELLOW_COLOR
	rESET_COLOR
	wHITE_COLOR
	cYAN_COLOR
)
const buffer_size uint = 10

type Dependencie struct {
	name    string
	version string
	status  string
}

type PackageJson struct {
	Name         string            `json:"name"`
	Version      string            `json:"version"`
	Description  string            `json:"description"`
	Main         string            `json:"main"`
	Jstype       string            `json:"type"`
	Scripts      map[string]string `json:"scripts"`
	Author       string            `json:"author"`
	License      string            `json:"license"`
	Dependencies map[string]string `json:"dependencies"`
}

func newPackageJson(name string, desc string, main string, jsType string, scripts map[string]string, author string, depends map[string]string) *PackageJson {
	return &PackageJson{
		Name:         name,
		Version:      "1.0",
		Description:  desc,
		Main:         main,
		Jstype:       jsType,
		Scripts:      scripts,
		Author:       author,
		License:      "ISC",
		Dependencies: depends,
	}

}

// the structure the confing needs to be in before seralization
type TsConfig struct {
	CompilerOptions *Config  `json:"compilerOptions"`
	Include         []string `json:"include"`
}

// the embeded struct for the tsConfig struct, will hold all of the config options for the tsconfig
type Config struct {
	Target             string `json:"target"`
	Module             string `json:"module"`
	Strict             bool   `json:"strict"`
	RemoveComments     bool   `json:"removeComments"`
	PreserveConstEnums bool   `json:"preserveConstEnums"`
	OutDir             string `json:"outDir"`
	NoImplicitAny      bool   `json:"noImplicitAny"`
}

func newConfig() *Config {
	return &Config{
		Target:             "es2021",
		Module:             "",
		Strict:             false,
		RemoveComments:     false,
		PreserveConstEnums: false,
		OutDir:             "",
		NoImplicitAny:      false,
	}
}

func newTsconfig() *TsConfig {
	c := newConfig()
	return &TsConfig{
		CompilerOptions: c,
		Include:         []string{"src/**/*"},
	}
}

type Generator struct {
	args            []string
	Path            string
	name            string
	desc            string
	author          string
	jsType          string
	dependices      []string
	errorsLock      sync.RWMutex
	errorDependcies chan Dependencie
	isTypescript    bool
	depchan         chan Dependencie
	// doneChan        chan int
	wg sync.WaitGroup
}

func (g *Generator) flagsCheck() bool {
	return len(g.args) >= 2 && (g.args[1] == "-d" || g.args[1] == "--default")
}

func (g *Generator) defaultGenerator() {
	p, _ := os.Getwd()
	path := filepath.Join(p, "express-app")
	g.Path = path
	g.name = "user"
	g.desc = "default express app"
	g.author = "user"
	g.jsType = "module"
	g.dependices = []string{"express", "dotenv"}
	g.isTypescript = false
	g.createProject()
}

func (g *Generator) getProjectHome() (string, error) {
	var choice string
	var io string
	ColoredPrint(wHITE_COLOR, "relaitve or absolute path for the project?")
	_, err := fmt.Scan(&choice)
	if err != nil {
		return "", err
	}
	printable, comperr := Compare("relative", "absolute", &choice)
	if comperr != nil {
		return "", comperr
	}
	ColoredPrint(wHITE_COLOR, "where would you like the project to live?")
	_, err = fmt.Scan(&io)
	if err != nil {
		return "", err
	}
	inputErr := ValidUserInput(choice, io, printable)
	if inputErr != nil {
		return "", inputErr
	}
	p, _ := os.Getwd()
	path := filepath.Join(p, io)
	if printable == "relative" {
		return filepath.Join(path, "src"), nil
	}
	return filepath.Join(io, "src"), nil

}

func (g *Generator) getProjectName() (string, error) {
	var io string
	ColoredPrint(wHITE_COLOR, "what is the name of the project?")
	_, err := fmt.Scan(&io)
	if err != nil {
		return "", err
	}
	if err := ValidUserInput(io); err != nil {
		return "", err
	}
	ClearScreen()
	ColoredPrint(cYAN_COLOR, "project name -> "+io)
	return io, nil
}
func (g *Generator) getAuthor() (string, error) {
	var io string
	ColoredPrint(wHITE_COLOR, "who is the author of this project")
	_, err := fmt.Scan(&io)
	if err != nil {
		return "", err
	}
	if err := ValidUserInput(io); err != nil {
		return "", err
	}
	ClearScreen()
	ColoredPrint(cYAN_COLOR, "project author -> "+io)
	return io, nil
}

func (g *Generator) getDepends() ([]string, error) {
	ClearScreen()
	ColoredPrint(wHITE_COLOR, "please enter the additonal dependcies for your project(express and dotenv included)")
	ColoredPrint(yELLOW_COLOR, "\nmake sure to end list with <space>/\nif you wish to have no aditional dependcies just type <space>/")
	array, err := Readinput(bufio.NewScanner(os.Stdin))
	//allow for the empty list of deps, and just return the default deps
	if err != nil && ErrorMessageCompare(err.Error(), "no aditional dependicies provided") {
		ColoredPrint(yELLOW_COLOR, err.Error())
		return g.dependices, nil
	}
	//append will concat the 2 slices and return a new slice, the ... is kinda like the
	// spreade operator in js
	return append(g.dependices, array...), nil
}

func (g *Generator) getDesc() (string, error) {
	var io string
	ColoredPrint(wHITE_COLOR, "what is the description of the project?")
	_, err := fmt.Scan(&io)
	if err != nil {
		return "", err
	}
	if err := ValidUserInput(io); err != nil {
		return "", err
	}
	ClearScreen()
	ColoredPrint(cYAN_COLOR, "project desc -> "+io)
	return io, nil
}
func (g *Generator) getJsType() (string, error) {
	var io string
	ColoredPrint(wHITE_COLOR, "what type module type do you want to use?\n Module(m) or CommonJS(c)?")
	_, err := fmt.Scan(&io)
	if err != nil {
		return "", err
	}
	if err := ValidUserInput(io); err != nil {
		return "", err
	}
	jsType, jsError := Compare("module", "commonjs", &io)
	if jsError != nil {
		return "", jsError
	}
	ClearScreen()
	ColoredPrint(cYAN_COLOR, "js type -> "+jsType)
	return jsType, nil
}

func (g *Generator) jsOrTs() (bool, error) {
	var io string
	ClearScreen()
	ColoredPrint(wHITE_COLOR, "would you like to use javascript or typescript?")
	if _, err := fmt.Scan(&io); err != nil {
		return false, err
	}
	if err := ValidUserInput(io); err != nil {
		return false, err
	}
	val, err := Compare("typescript", "javascript", &io)
	if err != nil {
		return false, err
	}
	ColoredPrint(cYAN_COLOR, fmt.Sprintf("script type -> %s ", val))
	if val == "typescript" {
		return true, nil
	} else {
		return false, nil
	}
}

func (g *Generator) userGenerator() {
	//find a better way to handle these errors
	var err error
	// might replace the panics with error handlers
	g.Path, err = g.getProjectHome()
	if err != nil {
		if !HandleError(err) {
			HandleExit(0)
		}
		ColoredPrint(yELLOW_COLOR, "will be using the defalut dir")
		dir, _ := os.Getwd()
		g.Path = filepath.Join(dir, "express-app", "src")
		// panic("error when creating the project home")
	}
	ClearScreen()
	ColoredPrint(cYAN_COLOR, "project path -> "+g.Path)
	g.name, err = g.getProjectName()
	if err != nil {
		ColoredPrint(rED_COLOR, err.Error())
		panic("error when getting project name")
	}
	g.desc, err = g.getDesc()
	if err != nil {
		ColoredPrint(rED_COLOR, err.Error())
		panic("error when getting project desc")
	}
	g.author, err = g.getAuthor()
	if err != nil {
		ColoredPrint(rED_COLOR, err.Error())
		panic("error when getting the author")
	}
	g.jsType, err = g.getJsType()
	if err != nil {
		ColoredPrint(rED_COLOR, err.Error())
		panic("error when getting the module type for js")
	}
	g.isTypescript, err = g.jsOrTs()
	if err != nil {
		ColoredPrint(yELLOW_COLOR, "problem when getting the js or ts type!!\n will be using javascript by default!\n")
		g.isTypescript = false
	}

	g.dependices, err = g.getDepends()
	if err != nil {
		ColoredPrint(rED_COLOR, err.Error())
		panic("error when getting the dependicies")
	}
	g.createProject()
	if err != nil {
		ColoredPrint(rED_COLOR, err.Error())
		panic("problem when creating the project")
	}
	g.displayFinalMessage()
}

func (g *Generator) displayErrorDepends() {
	for v := range g.errorDependcies {
		ColoredPrint(rED_COLOR, fmt.Sprintf("%+v %+v!\n please check the npm site to see if entered dependcie is avalable for download!!", v.name, v.status))
	}

}

func (g *Generator) displayFinalMessage() {
	ClearScreen()
	n := len(g.errorDependcies)
	emsg := fmt.Sprintf("WARNING:\n %d of your entered dependcies were not found when creating the project!\n", n)
	gmsg := "Project has been generated!\n HAVE FUN CODING!!!"
	if n == 0 {
		ColoredPrint(gREEN_COLOR, gmsg)
	} else {
		ColoredPrint(rED_COLOR, emsg)
		g.displayErrorDepends()
	}

}

func (g *Generator) creatEnvFile() error {
	ColoredPrint(gREEN_COLOR, "creating the .env file...")
	currPath := filepath.Join(g.Path, ".env")
	if Exists(currPath) {
		return errors.New("a git ignore file already exists in the place you wish to create")
	}
	file, fileErr := os.OpenFile(currPath, os.O_WRONLY|os.O_CREATE, os.ModePerm)
	if fileErr != nil {
		return fileErr
	}
	_, err := file.Write([]byte("DB_URI=?\nPORT=8080\n"))
	if err != nil {
		return err
	}
	if err := file.Close(); err != nil {
		return err
	}
	return nil

}

func (g *Generator) createGitIgnore() error {
	ColoredPrint(gREEN_COLOR, "creating the gitignore file...")
	currPath := filepath.Join(g.Path, ".gitignore")
	if Exists(currPath) {
		return errors.New("a git ignore file already exists in the place you wish to create")
	}
	file, fileErr := os.OpenFile(currPath, os.O_WRONLY|os.O_CREATE, os.ModePerm)
	if fileErr != nil {
		return fileErr
	}
	var writeError error
	if g.isTypescript {
		_, writeError = file.Write([]byte("./tsconfig.json\n"))
		if writeError != nil {
			return writeError
		}
	}
	_, writeError = file.Write([]byte("./package.json\n ./env\n"))
	if writeError != nil {
		return writeError
	}
	if err := file.Close(); err != nil {
		return err
	}
	return nil

}

func (g *Generator) createControllersDir() error {
	currPath := filepath.Join(g.Path, "controllers")
	if Exists(currPath) {
		return errors.New("the controllers dir already exitsts, cannot create")
	}
	if err := os.Mkdir(currPath, os.ModePerm); err != nil {
		return err
	}
	return nil
}
func (g *Generator) createRoutesDir() error {
	currPath := filepath.Join(g.Path, "routes")
	if Exists(currPath) {
		return errors.New("the routes dir already exitsts, cannot create")
	}
	if err := os.Mkdir(currPath, os.ModePerm); err != nil {
		return err
	}
	return nil
}
func (g *Generator) buildDstDir() error {
	currPath := filepath.Join(g.Path, "../dist")
	if Exists(currPath) {
		return errors.New("the routes dir already exitsts, cannot create")
	}
	if err := os.Mkdir(currPath, os.ModePerm); err != nil {
		return err
	}
	return nil
}

func (g *Generator) createProjectHome() error {
	if Exists(g.Path) {
		return errors.New("the home dir already exitsts, cannot create")
	}
	if err := os.MkdirAll(g.Path, os.ModePerm); err != nil {
		return err
	}
	return nil
}

func (g *Generator) createIndexFile() error {
	var ending string
	if g.isTypescript {
		ending = ".ts"
	} else {
		ending = ".js"
	}
	indexPath := filepath.Join(g.Path, fmt.Sprintf("index%s", ending))
	if Exists(indexPath) {
		return errors.New("index file in this dir already exists")
	}
	file, fileError := os.OpenFile(indexPath, os.O_WRONLY|os.O_CREATE, os.ModePerm)
	if fileError != nil {
		return fileError
	}
	if g.jsType == "commonjs" {
		_, writeError := file.Write([]byte("const dotenv = require('dotenv').config()\nconst express = require('express')\n\n\n"))
		if writeError != nil {
			return writeError
		}
	} else {
		_, writeError := file.Write([]byte("import * as dotenv from 'dotenv';\nimport express from 'express'\n\n\n"))
		if writeError != nil {
			return writeError
		}
	}
	_, writeError := file.Write([]byte("const app = express()\n\napp.use(json())\n\napp.listen(process.env.PORT|| 5000, ()=> console.log('server is running'))\n\n"))
	if writeError != nil {
		return writeError
	}
	if err := file.Close(); err != nil {
		return err
	}
	return nil
}

func (g *Generator) queryNpm(dep string) {
	ColoredPrint(gREEN_COLOR, fmt.Sprintf("quering for %s", dep))
	r, err := http.Get(fmt.Sprintf("https://api.npms.io/v2/search?q=%s", dep))
	if err != nil {
		return
	}
	version, err := ParseJsonResponse(r)
	if err != nil && err.Error() == "no hits on entered dependicies" {
		// the program is freezing when pushing into either of the channels
		g.errorDependcies <- Dependencie{
			name:    dep,
			version: "0.0.0",
			status:  "failed",
		}
		g.wg.Done()
		return
	}
	g.depchan <- Dependencie{
		name:    dep,
		version: version,
		status:  "found",
	}
	g.wg.Done()
}

func (g *Generator) handleDeps() {
	//fix: for some reason the request is hanging and not calling done so the
	//whole program is stuck
	for _, dep := range g.dependices {
		g.wg.Add(1)
		go g.queryNpm(dep)
	}
	g.wg.Wait()
	//make sure to close the channels so they do not contuinue to block the main thread
	close(g.depchan)
	close(g.errorDependcies)

}

func (g *Generator) createPackageJson() error {
	scripts := make(map[string]string)
	scripts["test"] = "echo"
	if HasItem(g.dependices, "nodemon") {
		scripts["start"] = "nodemon index.js"
	}
	if g.isTypescript {
		scripts["build"] = "tsc build"
		scripts["run"] = "node dist/index.js"
	}
	//will iterate and make the request for all of the dependcies
	g.handleDeps()
	fmt.Println("made it out of the handle deps function")
	//use wait to hold until all of the deps have been queried for
	mapper := make(map[string]string)
	//conver the dep type into the needed map for the tsconfig
	for d := range g.depchan {
		fmt.Println("adding ", d, "to the mapper")
		mapper[d.name] = d.version
	}
	//needs to be seralized
	fmt.Println("serializing the package.json")
	jsPackage := newPackageJson(g.name, g.desc, "index.js", g.jsType, scripts, g.author, mapper)
	serailized, err := json.Marshal(jsPackage)
	if err != nil {
		return err
	}
	currPath := filepath.Join(g.Path, "package.json")
	if Exists(currPath) {
		return errors.New("a package.json already exitsts in this dir")
	}
	file, fileError := os.OpenFile(currPath, os.O_WRONLY|os.O_CREATE, os.ModePerm)
	if fileError != nil {
		return fileError
	}
	if _, err := file.Write(serailized); err != nil {
		return err
	}
	if err := file.Close(); err != nil {
		return err
	}
	return nil
}

func (g *Generator) buildTsconfig() error {
	ts := newTsconfig()
	//enter all of the config options
	if g.jsType == "commonjs" {
		ts.CompilerOptions.Module = "Commonjs"
	} else {
		ts.CompilerOptions.Module = "ES6"
	}
	ts.CompilerOptions.Strict = true
	ts.CompilerOptions.RemoveComments = false
	ts.CompilerOptions.PreserveConstEnums = true
	ts.CompilerOptions.OutDir = "dist"
	ts.CompilerOptions.NoImplicitAny = true

	//seralize the data
	seralized, err := json.Marshal(ts)
	if err != nil {
		return err
	}
	currPath := filepath.Join(g.Path, "../tsconfig.json")
	if Exists(currPath) {
		return errors.New("tsconfig already exists in this dir")
	}
	file, fErr := os.OpenFile(currPath, os.O_WRONLY|os.O_CREATE, os.ModePerm)
	if fErr != nil {
		return fErr
	}
	if _, err := file.Write(seralized); err != nil {
		return err

	}
	if err := file.Close(); err != nil {
		return err
	}
	return nil
}

func (g *Generator) handleCommnadsInstall() error {
	tsCommands := exec.Command("npm", "install typescript --save-dev && install --save @types/express")
	noSpecificCommands := exec.Command("npm", "install")
	//need this so the commands prints will be displayed when they are called
	tsCommands.Stdout = os.Stdout
	noSpecificCommands.Stdout = os.Stdout
	if err := os.Chdir(g.Path); err != nil {
		return fmt.Errorf("unknown error when changing dir: %v", err)
	}
	if g.isTypescript {
		if err := tsCommands.Run(); err != nil {
			return fmt.Errorf("error when running the typescript commands: %v", err)
		}
	}
	if err := noSpecificCommands.Run(); err != nil {
		return fmt.Errorf("error when running the general commands: %v", err)
	}
	return nil

}

func (g *Generator) createProject() {
	var err error
	err = g.createProjectHome()
	if err != nil {
		panic(err.Error())
	}
	err = g.creatEnvFile()
	if err != nil {
		panic(err.Error())
	}
	err = g.createGitIgnore()
	if err != nil {
		panic(err.Error())
	}
	g.createIndexFile()
	g.createPackageJson()
	err = g.createControllersDir()
	if err != nil {
		panic(err.Error())
	}
	err = g.createRoutesDir()
	if err != nil {
		panic(err.Error())
	}
	if g.isTypescript {
		g.buildTsconfig()
		g.buildDstDir()
	}
	g.handleCommnadsInstall()
}

func (g *Generator) Build() {
	if g.flagsCheck() {
		ColoredPrint(cYAN_COLOR, "default build chosen")
		g.defaultGenerator()
	} else {
		g.userGenerator()
	}
}
func NewGenerator() *Generator {
	path, _ := os.Getwd()
	return &Generator{
		args:            os.Args,
		Path:            path,
		name:            "",
		desc:            "",
		author:          "",
		jsType:          "",
		dependices:      []string{"express", "dotenv"},
		errorsLock:      sync.RWMutex{},
		errorDependcies: make(chan Dependencie, buffer_size),
		isTypescript:    false,
		//make sure to buffer the dep chan to make it not blocking
		depchan: make(chan Dependencie, buffer_size),
		//make sure this one is blocking
		// doneChan: make(chan int),
		wg: sync.WaitGroup{},
	}
}
