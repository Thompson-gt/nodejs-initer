package Generator

// this file will just be a small util lib for the small fucntions
// used inside of the generator

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

// alias for the color enum
type Color int

// const (
// 	rED_COLOR    = "\u001b[31m"
// 	gREEN_COLOR  = "\u001b[32m"
// 	yELLOW_COLOR = "\u001b[33m"
// 	rESET_COLOR  = "\u001b[0m"
// 	wHITE_COLOR  = "\u001b[37m"
// 	cYAN_COLOR   = "\u001b[36m"
// )

// function that takes in a color from the enum and
// returns the correct ansi code for the given color
// will panic if given a invalid color
func GetColor(c Color) string {
	switch c {
	case rED_COLOR:
		return "\u001b[31m"
	case gREEN_COLOR:
		return "\u001b[32m"
	case yELLOW_COLOR:
		return "\u001b[33m"
	case rESET_COLOR:
		return "\u001b[0m"
	case wHITE_COLOR:
		return "\u001b[37m"
	case cYAN_COLOR:
		return "\u001b[36m"
	default:
		panic("no valid color given")
	}
}

// checks if file or path exits
func Exists(filepath string) bool {
	_, err := os.Stat(filepath)
	if err == nil {
		return true
	}
	if os.IsExist(err) {
		return true
	}
	return false
}

// will print the given message with the specified color
func ColoredPrint(color Color, msg string) {
	if len(msg) <= 0 {
		panic("invalid message passed to ColoredPrint")
	}
	fmt.Println(GetColor(color) + msg + GetColor(rESET_COLOR))

}

// used to compare the first character of the inputed value against
// the 2 options, will return error if netiher match
func Compare(option1 string, option2 string, input *string) (string, error) {
	var out string
	i := string(*input)
	if string(i[0]) == string(option1[0]) || string(i[0]) == strings.ToLower(string(option1[0])) {
		out = option1
		return out, nil
	} else if string(i[0]) == string(option2[0]) || string(i[0]) == strings.ToLower(string(option2[0])) {
		out = option2
		return out, nil
	}
	return "", errors.New("input doesnt match either of the strings")
}

// variadic fucntion to take in list of strings and check if they are valid
func ValidUserInput[T ~string | ~[]string](inputs ...T) error {
	for _, val := range inputs {
		if len(val) <= 0 {
			return errors.New("user input must not be empty")
		}
	}
	return nil
}

// will use ansi codes clear the screen, should work on all os's
func ClearScreen() {
	fmt.Print("\033[H\033[2J")
}

func HasItem[T ~int | ~string | ~uint](list []T, val T) bool {
	for _, l := range list {
		if l == val {
			return true
		}
	}
	return false

}

// fucntion to take in the respose of a dependcie request and return the version type of the given package
func ParseJsonResponse(repsonse *http.Response) (string, error) {
	body, _ := io.ReadAll(repsonse.Body)
	//this is the type the json message will come in as
	var f map[string]interface{}
	json.Unmarshal(body, &f)
	//check if the given dependcie was found
	if len(f["results"].([]interface{})) <= 0 {
		return "", errors.New("no hits on entered dependicies")
	}
	resultsMap := f["results"].([]interface{})[0]
	closer := resultsMap.(map[string]interface{})["package"]
	//make sure to cast the any type to string
	return closer.(map[string]interface{})["version"].(string), nil
}

// a func to take in the scanner and return the array of entered data from the given scanner
func Readinput(s *bufio.Scanner) ([]string, error) {
free:
	for s.Scan() {
		array := strings.Split(s.Text(), " ")
		if len(array) >= 1 && array[0] == "/" {
			break free
		}
		if array[len(array)-1] == "/" {
			return array[0 : len(array)-1], nil
		}
	}
	return nil, errors.New("no aditional dependicies given")
}

// helper func to compare the errors using their messages
func ErrorMessageCompare(err1 string, err2 string) bool {
	if err1 == err2 {
		return true
	} else {
		return false
	}
}

// a helper funcion to prompt the user if they want to handle the error or to exit the program
func HandleError(e error) bool {
	var io string
	ColoredPrint(rED_COLOR, fmt.Sprintf("error: %v \n would you like for the error to be handled? with built in measures?\n", e))
	//dont handle error if error when handling
	if _, err := fmt.Scan(&io); err != nil {
		return false
	}
	if err := ValidUserInput(io); err != nil {
		return false
	}
	answer, answerError := Compare("yes", "no", &io)
	if answerError != nil {
		return false
	}
	if answer == "yes" {
		return true
	} else {
		return false
	}

}

// helper fucntion to handle the end of the program and print the code it was exited with
func HandleExit(code int) {
	ColoredPrint(gREEN_COLOR, fmt.Sprintf("the program has been exited with the following code:%d", code))
	os.Exit(code)
}
