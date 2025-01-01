
def register(options_templates, options_section, OptionInfo):
    options_templates.update(options_section((None, "Forge Hidden options"), {
        "forge_unet_storage_dtype": OptionInfo('Automatic'),
        "forge_inference_memory": OptionInfo(1024),
        "forge_async_loading": OptionInfo('Queue'),
        "forge_pin_shared_memory": OptionInfo('CPU'),
        "forge_lora_merge_type" : OptionInfo('merge'),
        "forge_preset": OptionInfo('sd'),
        "forge_additional_modules": OptionInfo([]),
    }))
