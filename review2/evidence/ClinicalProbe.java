import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.lang.reflect.*;
import java.util.*;
import org.apache.pdfbox.pdmodel.*;
import org.apache.pdfbox.pdmodel.graphics.image.LosslessFactory;
import org.aideway.document.pdf.PdfExtractionConfiguration;
import org.aideway.workflow.message.types.file.FileMessage;
import org.aideway.workflow.nodes.types.transform.markdown.FileMarkdownConverter;

/** Synthetic, local-only checks; invokes the compiled production implementation. */
public class ClinicalProbe {
  public static void main(String[] args) throws Exception {
    BufferedImage raster = new BufferedImage(800, 200, BufferedImage.TYPE_INT_RGB);
    Graphics2D g = raster.createGraphics();
    g.setColor(Color.WHITE); g.fillRect(0, 0, 800, 200); g.setColor(Color.BLACK);
    g.setFont(new Font("SansSerif", Font.PLAIN, 22));
    g.drawString("SYNTHETIC REVIEW TEST - no patient data", 20, 60);
    g.drawString("Unexpected significant finding requires review.", 20, 110); g.dispose();
    byte[] bytes;
    try (PDDocument pdf = new PDDocument(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
      PDPage page = new PDPage(); pdf.addPage(page);
      try (PDPageContentStream stream = new PDPageContentStream(pdf, page)) {
        stream.drawImage(LosslessFactory.createFromImage(pdf, raster), 20, 500, 570, 143);
      }
      pdf.save(out); bytes = out.toByteArray();
    }
    var config = new PdfExtractionConfiguration();
    var converted = FileMarkdownConverter.INSTANCE.toMarkdown(new FileMessage("SYNTHETIC-review.pdf", "application/pdf", bytes), config);
    System.out.println("imageOnlyPdf: inputBytes=" + bytes.length + ", tesseractConfigured=" + (config.getTesseractPath() != null) + ", outputCharacters=" + converted.toText().length());
    var empty = FileMarkdownConverter.INSTANCE.toMarkdown(new FileMessage("SYNTHETIC-empty.pdf", "application/pdf", new byte[0]), config);
    System.out.println("zeroBytePdf: outputCharacters=" + empty.toText().length());
    Class<?> responseClass = Class.forName("org.tekfive.polyglot.ChatResponse");
    Class<?> targetClass = Class.forName("org.tekfive.polyglot.ModelTarget");
    Class<?> partClass = Class.forName("org.tekfive.polyglot.ContentPart$Text");
    Class<?> finishClass = Class.forName("org.tekfive.polyglot.FinishReason");
    Class<?> nodeClass = Class.forName("org.aideway.workflow.nodes.types.transform.analyze.file.AnalyzeFileNodeType$V1");
    Method resultMethod = nodeClass.getDeclaredMethod("responseResult", responseClass); resultMethod.setAccessible(true);
    Object node = nodeClass.getField("INSTANCE").get(null);
    System.out.println("targetConstructors=" + Arrays.toString(targetClass.getConstructors()));
    // Constructor is filled reflectively to avoid relying on Kotlin synthetic defaults.
    Object target = null;
    for (Constructor<?> c : targetClass.getConstructors()) {
      if (c.getParameterCount() == 2 && c.getParameterTypes()[0] == String.class) target = c.newInstance("synthetic", "synthetic");
      if (c.getParameterCount() == 1 && c.getParameterTypes()[0] == String.class) target = c.newInstance("synthetic");
      if (c.getParameterCount() == 3 && c.getParameterTypes()[0] == String.class) target = c.newInstance("synthetic", "synthetic", null);
    }
    if (target == null) throw new IllegalStateException("Inspect ModelTarget constructor");
    Object usage = Class.forName("org.tekfive.polyglot.Usage").getConstructor().newInstance();
    for (String finish : new String[]{"STOP", "MAX_TOKENS"}) {
      Object response = null;
      for (Constructor<?> c : responseClass.getConstructors()) if (c.getParameterCount() == 8) {
        response = c.newInstance(target, java.util.List.of(partClass.getConstructor(String.class).newInstance("{}")), usage, Enum.valueOf((Class)finishClass, finish), null, Map.of(), null, null);
      }
      Object result = resultMethod.invoke(node, response);
      System.out.println("emptyObjectResponse: finish=" + finish + ", result=" + result.getClass().getSimpleName());
    }
  }
}
