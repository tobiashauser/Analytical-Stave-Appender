# Analytical Stave Appender

![](assets/zwerg.jpg)

## How to install?

Conveniently install the tool with `pip` and use it from your command line:

```
pip install add_staves
```

### Windows

Make sure `python` is installed on your machine. This can be tested from the
terminal with:

```
python --version
```

If it isn't installed yet, you will be prompted to install it from the Store.
After the installation, pip will output a warning if its installation directory
is not available in the global PATH. 

> [!Note] 
> I don't have access to a Windows machine.. I hope it works in most cases.

<details>
    <summary>Adding a path to PATH</summary>
<ol>
<li><p>Open the Start menu and search for &#8220;Edit the system environment variables&#8221;, or type &#8220;Environment Variables&#8221; into the search bar and select &#8220;Edit the system environment variables&#8221; from the results.</p></li>
<li><p>In the System Properties window, click on the &#8220;Environment Variables&#8230;&#8221; button.</p></li>
<li><p>In the Environment Variables window, under the &#8220;System variables&#8221; section, locate the variable named &#8220;Path&#8221; and select it. Then, click on the &#8220;Edit&#8230;&#8221; button.</p></li>
<li><p>In the Edit Environment Variable window, click on the &#8220;New&#8221; button.</p></li>
<li><p>Enter the path you want to add in the provided field. Make sure to type the directory containing the executable files you want to access globally.</p></li>
<li><p>Click &#8220;OK&#8221; to close each of the open windows.</p></li>
<li><p>Restart your shell, in order for the new path to be picked up.</p></li>
</ol>
</details>
<details>
    <summary>Einen Pfad zu PATH hinzufügen</summary>
<ol>
<li><p>Öffnen Sie das Startmenü und suchen Sie nach &#8220;Systemumgebungsvariablen bearbeiten&#8221; oder geben Sie &#8220;Umgebungsvariablen&#8221; in die Suchleiste ein und wählen Sie &#8220;Umgebungsvariablen für Ihr Konto bearbeiten&#8221; aus.</p></li>
<li><p>Im Fenster &#8220;Umgebungsvariablen&#8221; unter dem Abschnitt &#8220;Systemvariablen&#8221; suchen Sie nach &#8220;Path&#8221; und klicken Sie darauf, um es zu markieren. Klicken Sie dann auf &#8220;Bearbeiten&#8230;&#8221;.</p></li>
<li><p>Klicken Sie im Fenster &#8220;Systemvariablen bearbeiten&#8221; auf &#8220;Neu&#8221;.</p></li>
<li><p>Geben Sie den Pfad ein, den Sie hinzufügen möchten, und klicken Sie auf &#8220;OK&#8221;.</p></li>
<li><p>Klicken Sie auf &#8220;OK&#8221;, um das Fenster &#8220;Umgebungsvariablen&#8221; zu schließen, und dann erneut auf &#8220;OK&#8221;, um das Fenster &#8220;Systemeigenschaften&#8221; zu schließen.</p></li>
<li><p>Starten Sie die Eingabeaufforderung neu, damit der Pfad aktualisiert wird.</p></li>
</ol>
</details>

### Briss

Briss depends on a Java runtime. When you open it you will be prompted to install it (if it's not already on your system).

## Usage

```
add-staves path/to/your/score.pdf
```

Further information about its usage can be found in its help: `add-staves --help`.

## Separate a score into systems

You can use any program of your choice in order to separate a score into systems.

> [!Important] 
> Make sure that each system or part you want to append analytical staves to,
> is its own page in the PDF.

The following tool works quite well, but any other suggestions are 
much appreciated.

### Briss

[BRISS](https://briss.sourceforge.net/) is a cross-platform application for 
cropping PDF-files. By default, it will try to find common areas on all the
pages and overlay them in the interface, so that you only have to declare 
the area to crop once and not on all pages. However, this doesn't work 
particularly well for scores. This behaviour can be circumvented by passing 
a range from the first to the last page (e.g. "1-4") to the dialog showing
immediately after loading a document.

#### Installation

On a mac, `briss` can be installed and started from the command line with:

```
brew install briss
briss path/to/score.pdf
```

For usage on Windows, an executable can be downloaded [here](https://sourceforge.net/projects/briss/files/latest/download). After unzipping, double-clicking will
launch Briss. 

> [!Note]
> Briss needs a Java runtime to be installed on the system. You will prompted to 
> install it if it doesn't exist.
