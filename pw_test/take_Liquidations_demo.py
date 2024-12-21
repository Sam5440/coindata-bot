from playwright.sync_api import sync_playwright
from PIL import Image
import os


class ScreenshotManager:
    def __init__(
        self,
        url,
        screenshot_paths={},
        viewport={"width": 2000, "height": 3000},
        device_scale_factor=2.2,
    ):
        """
        初始化ScreenshotManager类。
        :param url: 要截图的页面URL。
        :param screenshot_paths: 一个字典，包含截图的保存路径和对应的元素选择器。
        """
        self.url = url
        self.screenshot_paths = screenshot_paths
        for k,v in self.screenshot_paths.items():
            if not v.startswith("."):
                self.screenshot_paths[k] = self.class2selector(v)
        self.viewport = viewport
        self.device_scale_factor = device_scale_factor

    def browser_control(self,func_list):
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(
                viewport=self.viewport, device_scale_factor=self.device_scale_factor
            )
            page = context.new_page()
            try:
                page.goto(self.url)
                page.wait_for_load_state("networkidle")
            # 截图操作
                for func in func_list:
                    func(page)
            # 截图操作结束
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                context.close()
                browser.close()
    def take_class_image(self, page):
        """
        在页面上捕获指定类的元素截图，并将其拼接成一个完整的图片。

        :param page: Playwright的Page对象，表示当前的页面。
        """
        # 遍历截图路径字典中的每个元素
        for filename, selector in self.screenshot_paths.items():
            elements = page.query_selector_all(selector)
            if elements:
                screenshots = self.capture_screenshots(elements, filename)
                self.merge_images(screenshots, filename)
                self.cleanup_screenshots(screenshots)
            else:
                print(f"No elements found with selector '{selector}'.")
                
    def capture_screenshots(self, elements, filename_prefix):
        """
        捕获并保存元素的截图。

        :param elements: 要截图的元素列表。
        :param filename_prefix: 截图文件名的前缀。
        :return: 截图文件路径列表。
        """
        screenshots = []
        for i, element in enumerate(elements):
            screenshot_path = f"{filename_prefix}_{i}.png"
            element.screenshot(path=screenshot_path)
            screenshots.append(screenshot_path)
        return screenshots

    def class2selector(self, class_name):
        """
        此函数用于将类名转换为CSS选择器。

        :param class_name: 要转换的类名。
        :return: 转换后的CSS选择器。
        """
        return f".{class_name.replace(' ', '.')}"



    def merge_images(self, screenshots, output_path):
        """
        将多个图片拼接成一个完整的图片。

        :param screenshots: 截图文件路径列表。
        :param output_path: 输出图片的路径。
        """
        try:
            images = [Image.open(image) for image in screenshots]
            widths, heights = zip(*(i.size for i in images))
            total_height = sum(heights)
            max_width = max(widths)
            new_image = Image.new("RGB", (max_width, total_height))
            print("new_image is created")
            y_offset = 0
            for image in images:
                new_image.paste(image, (0, y_offset))
                y_offset += image.height
            # print("new_image is saved")
            new_image.save(output_path)
            print("new_image is saved")
        except Exception as e:
            print(f"An error occurred while merging images: {e},try to save [{output_path}] is failed")
            # 可以在这里添加更多的日志记录或调试信息

    def cleanup_screenshots(self, screenshots):
        """
        删除截图文件。
        :param screenshots: 截图文件路径列表。
        """
        for screenshot in screenshots:
            os.remove(screenshot)


if __name__ == "__main__":
    screenshot_manager = ScreenshotManager(
        "https://www.coinglass.com/zh/pro/futures/Liquidations",
        {"Liquidations.png": "plr20"},
    )
    screenshot_manager.browser_control([screenshot_manager.take_class_image])
    # screenshot_manager.merge_images(["Liquidations.png", "LiquidationMap.png"], "m.png")
