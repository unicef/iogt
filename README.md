# goodinternet.org

This branch (`gh-pages`) contains the documentation site and CMS Manual for the IoGT project. This site is built using [Jekyll](https://jekyllrb.com), a static site generator. GitHub Pages supports Jekyll sites out-of-the-box, with no special configuration necessary. Read more about GitHub Pages [here](https://pages.github.com).

## Development

There are a couple steps required to set up a local development environment:

1. [Install Ruby, RubyGems, GCC, and Make](https://jekyllrb.com/docs/)
2. Install Bundler and Jekyll
3. Clone this repository
4. Launch a development server

### [Install Ruby, RubyGems, GCC, and Make](https://jekyllrb.com/docs/installation/#guides)

**A note on Windows**: Ruby has first-class support for all Unix-like operating systems, including macOS, Ubuntu, and other Linux distributions. Ruby and Jekyll does not officially support Windows, however there are a couple workarounds to get Ruby and Jekyll to work on Windows. See the Windows Guide on [this](https://jekyllrb.com/docs/installation/#guides) page for more information.

Ruby, RubyGems, GCC, and make can be install through your OS's package manager. On macOS, it is recommended you have [Homebrew](https://brew.sh) installed. Follow the shell commands below:

**macOS**
```zsh
# install command line tools
$ xcode-select --install

# set SDKROOT
$ export SDKROOT=$(xcrun --show-sdk-path)

# install Ruby via Homebrew
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
$ brew install ruby

# Update your PATH
# If you're using Zsh
$ echo 'export PATH="/usr/local/opt/ruby/bin:/usr/local/lib/ruby/gems/3.0.0/bin:$PATH"' >> ~/.zshrc
$ source ~/.zshrc

# If you're using Bash
$ echo 'export PATH="/usr/local/opt/ruby/bin:/usr/local/lib/ruby/gems/3.0.0/bin:$PATH"' >> ~/.bash_profile
$ source ~/.bash_profile

# Unsure which shell you are using? Type
echo $SHELL
```

**Ubuntu**
```bash
# Install Ruby, RubyGems, GCC, Make
$ sudo apt-get install ruby-full build-essential zlib1g-dev

# Create a seperate directory to store your gems, then source your ~/.bashrc
$ echo '# Install Ruby Gems to ~/gems' >> ~/.bashrc
$ echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
$ echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
$ source ~/.bashrc
```

**Other distributions**

For other Linux distrubtions, follow the instructions [here](https://jekyllrb.com/docs/installation/other-linux/).


### Install Bundler and Jekyll


Make sure your installation succeeded. Run the following commands. The comments following are how the output is supposed to look like. It will be different for you depending on your system and precise version.

```bash
$ ruby -v
# ruby 3.0.2p107 (2021-07-07 revision 0db68f0233) [x86_64-darwin21]

$ gem -v
# 3.2.22

$ gcc -v
# Configured with: --prefix=/Library/Developer/CommandLineTools/usr --with-gxx-include-dir=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/c++/4.2.1
# Apple clang version 13.0.0 (clang-1300.0.25.3)
# Target: x86_64-apple-darwin21.0.0
# Thread model: posix
# InstalledDir: /Library/Developer/CommandLineTools/usr/bin

$ g++ -v
# Configured with: --prefix=/Library/Developer/CommandLineTools/usr --with-gxx-include-dir=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/c++/4.2.1
# Apple clang version 13.0.0 (clang-1300.0.25.3)
# Target: x86_64-apple-darwin21.0.0
# Thread model: posix
# InstalledDir: /Library/Developer/CommandLineTools/usr/bin

$ make -v
# GNU Make 3.81
# Copyright (C) 2006  Free Software Foundation, Inc.
# This is free software; see the source for copying conditions.
# There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.
#
# This program built for i386-apple-darwin11.3.0
```

If all of these tools have been successfully installed, go ahead and install the Jekyll and Bundler gems:

```bash
$ gem install jekyll bundler
```

### Clone this repository

The GitHub Pages site is hosted on the `gh-pages` branch of the `unicef/iogt` repository.

```bash
# Clone over https
$ git clone https://github.com/unicef/iogt

# Clone over ssh
$ git clone git@github.com:unicef/iogt.git

# switch to the gh-pages branch
$ cd iogt
$ git switch gh-pages
$ git pull

$ bundle exec jekyll serve --watch -o
# Configuration file: /Users/pranav/Projects/iogt/_config.yml
#             Source: /Users/pranav/Projects/iogt
#        Destination: /Users/pranav/Projects/iogt/_site
#  Incremental build: disabled. Enable with --incremental
#       Generating... 
#                     done in 2.134 seconds.
#  Auto-regeneration: enabled for '/Users/pranav/Projects/iogt'
#     Server address: http://127.0.0.1:4000/
#   Server running... press ctrl-c to stop.
```

## Project Structure

The project is organized into several folders:

- `data/` - Contains structured data that is presented throughout the site
- `_includes` - HTML snippets that can be included modularly throughout the site
- `_layouts` - HTML page templates
- `_pages` - Where non-blog posts are stored. The CMS Manual is stored here
- `_posts` - Where blog posts are stored. We do not use blog posts so this directory is empty
- `_sass` - Where SCSS and CSS styles (typically from 3rd-party libraries such as Bootstrap) go. These are static assets and not processed by Jekyll beyond compilation of SCSS.
- `assets/css` - Where custom CSS and SCSS go. These files are processed by Jekyll (so Liquid tags and filters can be used). SCSS files are automatically compiled by Jekyll.
- `assets/img` - Images go here
  
There are also several root-level files that are important:
- `_config.yml` - Jekyll's configuration file
- `404.md` - This page will be served in place of a standard 404 error page
- `CNAME` - Custom domain name registration. _**Do not edit this file.**_
- `Gemfile` - A list of plugins installed by Ruby used in Jekyll. Comparable to Python's `requirements.txt` and NodeJS's `package.json`
- `index.md` - The homepage. The content of this page is created from `_layouts/home.html`