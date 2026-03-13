// Harvard Academic Resume Template
// Traditional academic style with serif font, monochrome black-only color,
// generous margins, and clean formatting per Harvard Career Services guidelines.
// Suitable for academic, executive, government, and formal industry roles.

// Read styling parameters from sys_inputs
#let font_family = sys.inputs.at("font_family", default: "EB Garamond")
#let font_size = eval(sys.inputs.at("font_size", default: "11pt"))
#let accent_color = rgb(sys.inputs.at("accent_color", default: "#000000"))
#let margin_size = eval(sys.inputs.at("margin", default: "1in"))
#let page_size = sys.inputs.at("page_size", default: "us-letter")
#let line_spacing = eval(sys.inputs.at("line_spacing", default: "0.65em"))
#let section_spacing = eval(sys.inputs.at("section_spacing", default: "0.9em"))

// Read resume content
#let resume_content = sys.inputs.at("resume_content", default: "")

// Page setup
#set page(
  paper: page_size,
  margin: (x: margin_size, y: margin_size),
)

// Text defaults
#set text(
  font: font_family,
  size: font_size,
  lang: "en",
  fill: luma(10),
)

// Paragraph settings
#set par(
  leading: line_spacing,
  justify: false,
)

// Heading styles
#show heading.where(level: 1): set text(
  size: 20pt,
  weight: "bold",
  fill: luma(0),
)
#show heading.where(level: 1): set align(center)
#show heading.where(level: 1): set block(below: 0.3em)

#show heading.where(level: 2): it => {
  v(section_spacing)
  block(below: 0.4em)[
    #text(
      size: font_size + 1pt,
      weight: "bold",
      fill: luma(0),
    )[#upper(it.body)]
    #v(-0.2em)
    #line(length: 100%, stroke: 0.5pt + luma(0))
  ]
}

#show heading.where(level: 3): it => {
  v(0.4em)
  text(
    size: font_size + 0.5pt,
    weight: "bold",
    fill: luma(0),
  )[#it.body]
}

// List styling
#set list(
  indent: 0.3em,
  body-indent: 0.5em,
  marker: text(size: 0.6em, fill: luma(0))[#sym.circle.filled],
)

// Link styling — black text to match monochrome aesthetic
#show link: set text(fill: luma(0))

// Document metadata
#set document(
  title: "Resume",
  date: datetime.today(),
)

// Render the resume content
#eval(resume_content, mode: "markup")
